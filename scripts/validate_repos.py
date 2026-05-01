#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import DATA_DIR, get_settings  # noqa: E402
from app.github_app import get_installation_token  # noqa: E402
from app.instructor_tools import (  # noqa: E402
    REPORTS_DIR,
    build_report,
    check_repo,
    get_assignment_slugs,
    get_whitelisted_usernames,
    repo_for,
    save_report,
)

ACCEPTED_ASSIGNMENTS_PATH = DATA_DIR / "accepted_assignments.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate expected GitHub Classroom repositories."
    )
    parser.add_argument(
        "--assignment",
        help="Validate one assignment slug instead of all assignments.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print expected repositories without calling GitHub or writing a report.",
    )
    return parser.parse_args()


def load_accepted_assignments(
    path: Path = ACCEPTED_ASSIGNMENTS_PATH,
) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    payload = json.loads(path.read_text())
    if isinstance(payload, list):
        return [record for record in payload if isinstance(record, dict)]
    if isinstance(payload, dict):
        records = payload.get("accepted_assignments")
        if isinstance(records, list):
            return [record for record in records if isinstance(record, dict)]
    raise ValueError(f"Invalid accepted assignments data: {path}")


def accepted_index(
    records: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        assignment_slug = record.get("assignment_slug")
        repo_name = record.get("repo_name")
        if isinstance(assignment_slug, str) and isinstance(repo_name, str):
            index[(assignment_slug, repo_name)] = record
    return index


def accepted_user_index(
    records: list[dict[str, Any]],
) -> dict[tuple[str, str], dict[str, Any]]:
    index: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        assignment_slug = record.get("assignment_slug")
        github_username = record.get("github_username")
        if isinstance(assignment_slug, str) and isinstance(github_username, str):
            index[(assignment_slug, github_username.lower())] = record
    return index


def accepted_match(
    assignment_slug: str,
    username: str,
    repo: str,
    by_repo: dict[tuple[str, str], dict[str, Any]],
    by_user: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any] | None:
    return by_repo.get((assignment_slug, repo)) or by_user.get(
        (assignment_slug, username.lower())
    )


def repo_report_labels(result: dict[str, Any]) -> dict[str, Any]:
    status = result["status"]
    expected_repo_status = {
        "exists": "expected repo exists",
        "missing": "expected repo missing",
        "permission_issue": "app lacks access",
    }.get(status, "repo check failed")
    return {
        "expected_repo_status": expected_repo_status,
        "app_access_status": (
            "app lacks access" if status == "permission_issue" else "app access ok"
        ),
    }


def accepted_report_labels(record: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "accepted_assignment_status": (
            "found in accepted assignments"
            if record
            else "not found in accepted assignments"
        ),
        "accepted_assignment": record,
    }


def validate_repos(assignment: str | None = None, dry_run: bool = False) -> dict:
    assignments = get_assignment_slugs(assignment)
    usernames = get_whitelisted_usernames()
    accepted_records = load_accepted_assignments()
    by_repo = accepted_index(accepted_records)
    by_user = accepted_user_index(accepted_records)
    entries = []

    if dry_run:
        for assignment_slug in assignments:
            for username in usernames:
                repo = repo_for(assignment_slug, username)
                accepted = accepted_match(
                    assignment_slug,
                    username,
                    repo,
                    by_repo,
                    by_user,
                )
                entries.append(
                    {
                        "assignment": assignment_slug,
                        "username": username,
                        "repo": repo,
                        "status": "dry_run",
                        "github_http_status": None,
                        "message": "Dry run; GitHub was not called.",
                        "expected_repo_status": "not checked",
                        "app_access_status": "not checked",
                        **accepted_report_labels(accepted),
                    }
                )
    else:
        settings = get_settings()
        token = get_installation_token(settings)
        for assignment_slug in assignments:
            for username in usernames:
                repo = repo_for(assignment_slug, username)
                result = check_repo(repo, token=token)
                accepted = accepted_match(
                    assignment_slug,
                    username,
                    repo,
                    by_repo,
                    by_user,
                )
                entries.append(
                    {
                        "assignment": assignment_slug,
                        "username": username,
                        **result,
                        **repo_report_labels(result),
                        **accepted_report_labels(accepted),
                    }
                )

    counts = Counter(entry["status"] for entry in entries)
    accepted_counts = Counter(
        entry["accepted_assignment_status"] for entry in entries
    )
    summary = {
        "assignments": len(assignments),
        "students": len(usernames),
        "total_checked": len(entries),
        "exists": counts.get("exists", 0),
        "missing": counts.get("missing", 0),
        "permission_issues": counts.get("permission_issue", 0),
        "app_lacks_access": counts.get("permission_issue", 0),
        "failures": counts.get("failure", 0),
        "accepted_assignments_file": str(ACCEPTED_ASSIGNMENTS_PATH),
        "accepted_assignments_loaded": len(accepted_records),
        "found_in_accepted_assignments": accepted_counts.get(
            "found in accepted assignments", 0
        ),
        "not_found_in_accepted_assignments": accepted_counts.get(
            "not found in accepted assignments", 0
        ),
        "dry_run": dry_run,
    }
    report = build_report(entries, summary)

    if not dry_run:
        save_report(REPORTS_DIR / "repo_validation_report.json", report)

    return report


def print_summary(report: dict) -> None:
    summary = report["summary"]
    print(f"Total checked: {summary['total_checked']}")
    print(f"Repo exists: {summary['exists']}")
    print(f"Repo missing: {summary['missing']}")
    print(
        "Found in accepted assignments: "
        f"{summary['found_in_accepted_assignments']}"
    )
    print(
        "Not found in accepted assignments: "
        f"{summary['not_found_in_accepted_assignments']}"
    )
    print(f"Permission issues: {summary['permission_issues']}")
    print(f"Failures: {summary['failures']}")
    if summary["dry_run"]:
        print("Dry run: no GitHub calls were made and no report was written.")
    else:
        print("Saved report to reports/repo_validation_report.json.")


def main() -> None:
    args = parse_args()
    try:
        report = validate_repos(args.assignment, dry_run=args.dry_run)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    print_summary(report)


if __name__ == "__main__":
    main()
