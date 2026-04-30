#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import get_settings  # noqa: E402
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


def validate_repos(assignment: str | None = None, dry_run: bool = False) -> dict:
    assignments = get_assignment_slugs(assignment)
    usernames = get_whitelisted_usernames()
    entries = []

    if dry_run:
        for assignment_slug in assignments:
            for username in usernames:
                repo = repo_for(assignment_slug, username)
                entries.append(
                    {
                        "assignment": assignment_slug,
                        "username": username,
                        "repo": repo,
                        "status": "dry_run",
                        "github_http_status": None,
                        "message": "Dry run; GitHub was not called.",
                    }
                )
    else:
        settings = get_settings()
        token = get_installation_token(settings)
        for assignment_slug in assignments:
            for username in usernames:
                repo = repo_for(assignment_slug, username)
                result = check_repo(repo, token=token)
                entries.append(
                    {
                        "assignment": assignment_slug,
                        "username": username,
                        **result,
                    }
                )

    counts = Counter(entry["status"] for entry in entries)
    summary = {
        "assignments": len(assignments),
        "students": len(usernames),
        "total_checked": len(entries),
        "exists": counts.get("exists", 0),
        "missing": counts.get("missing", 0),
        "permission_issues": counts.get("permission_issue", 0),
        "failures": counts.get("failure", 0),
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
