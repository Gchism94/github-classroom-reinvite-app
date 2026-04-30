#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.classroom_client import (  # noqa: E402
    GitHubClassroomClient,
    GitHubClassroomError,
    build_accepted_assignments_payload,
    normalize_accepted_assignment,
    normalize_classroom_assignment,
    save_accepted_assignments,
    save_assignments,
)
from app.config import get_settings  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync GitHub Classroom assignments into data/assignments.json."
    )
    parser.add_argument(
        "--classroom-id",
        help="GitHub Classroom ID. Defaults to GITHUB_CLASSROOM_ID.",
    )
    parser.add_argument(
        "--skip-accepted",
        action="store_true",
        help="Only sync assignment metadata, not accepted assignment repositories.",
    )
    return parser.parse_args()


def resolve_classroom_id(
    client: GitHubClassroomClient, configured_classroom_id: str | None
) -> str:
    if configured_classroom_id:
        return configured_classroom_id

    classrooms = client.list_classrooms()
    if len(classrooms) == 1:
        classroom_id = classrooms[0].get("id")
        if classroom_id:
            print(f"Using classroom {classroom_id}: {classrooms[0].get('name')}")
            return str(classroom_id)

    if classrooms:
        print("Multiple classrooms found. Re-run with --classroom-id or set GITHUB_CLASSROOM_ID.")
        for classroom in classrooms:
            print(f"- {classroom.get('id')}: {classroom.get('name')}")
    else:
        print("No classrooms were returned for the configured token.")

    raise SystemExit(1)


def sync_classroom(classroom_id: str | None, skip_accepted: bool = False) -> None:
    settings = get_settings()
    client = GitHubClassroomClient(settings=settings)
    classroom_id = resolve_classroom_id(
        client,
        classroom_id or settings.github_classroom_id,
    )

    raw_assignments = client.list_assignments(classroom_id)
    assignments = [
        assignment
        for assignment in (
            normalize_classroom_assignment(raw_assignment)
            for raw_assignment in raw_assignments
        )
        if assignment["id"] and assignment["slug"]
    ]
    save_assignments(assignments)
    print(f"Saved {len(assignments)} assignments to data/assignments.json.")

    if skip_accepted:
        return

    accepted_by_assignment: dict[str, list[dict]] = {}
    for assignment in assignments:
        assignment_id = str(assignment["id"])
        raw_accepted = client.list_accepted_assignments(assignment_id)
        accepted_by_assignment[assignment_id] = [
            normalize_accepted_assignment(accepted) for accepted in raw_accepted
        ]
        print(
            "Fetched "
            f"{len(accepted_by_assignment[assignment_id])} accepted repositories "
            f"for {assignment['slug']}."
        )

    save_accepted_assignments(
        build_accepted_assignments_payload(
            assignments,
            accepted_by_assignment,
            classroom_id,
        )
    )
    print("Saved accepted assignments to data/accepted_assignments.json.")


def main() -> None:
    args = parse_args()
    try:
        sync_classroom(args.classroom_id, skip_accepted=args.skip_accepted)
    except GitHubClassroomError as exc:
        print(f"Classroom sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
