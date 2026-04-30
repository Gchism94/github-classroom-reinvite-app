#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.audit import AUDIT_LOG_PATH  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read audit log entries.")
    parser.add_argument(
        "--limit",
        type=int,
        default=25,
        help="Number of recent entries to show.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw JSON log entries.",
    )
    return parser.parse_args()


def load_entries(limit: int) -> list[dict]:
    if not AUDIT_LOG_PATH.exists():
        return []

    lines = AUDIT_LOG_PATH.read_text().splitlines()
    selected_lines = lines[-limit:] if limit > 0 else lines
    entries: list[dict] = []
    for line in selected_lines:
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            entries.append({"message": "Invalid audit log line", "raw": line})
    return entries


def main() -> None:
    args = parse_args()
    entries = load_entries(args.limit)

    if args.json:
        for entry in entries:
            print(json.dumps(entry, sort_keys=True))
        return

    for entry in entries:
        print(
            "{timestamp} | {status} | {username} | {assignment} | {repo} | "
            "github={github_http_status} | {message}".format(
                timestamp=entry.get("timestamp", ""),
                status=entry.get("status", ""),
                username=entry.get("username", ""),
                assignment=entry.get("assignment", ""),
                repo=entry.get("repo", ""),
                github_http_status=entry.get("github_http_status", ""),
                message=entry.get("message", ""),
            )
        )


if __name__ == "__main__":
    main()
