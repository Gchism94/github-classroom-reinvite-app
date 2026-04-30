#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.classroom_client import GitHubClassroomClient, GitHubClassroomError  # noqa: E402


def main() -> None:
    try:
        client = GitHubClassroomClient()
        classrooms = client.list_classrooms()
    except GitHubClassroomError as exc:
        print(f"Could not list classrooms: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if not classrooms:
        print("No classrooms returned for this token.")
        return

    for classroom in classrooms:
        classroom_id = classroom.get("id", "")
        name = classroom.get("name", "")
        url = classroom.get("url") or classroom.get("html_url") or ""
        print(f"{classroom_id}\t{name}\t{url}")


if __name__ == "__main__":
    main()
