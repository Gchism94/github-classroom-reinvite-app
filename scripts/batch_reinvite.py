#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.audit import append_audit_log  # noqa: E402
from app.github_client import GitHubClientError, add_collaborator  # noqa: E402
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
        description="Batch restore write access for one GitHub Classroom assignment."
    )
    parser.add_argument(
        "--assignment",
        required=True,
        help="Assignment slug to process. Required for safety.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned reinvites without changing GitHub or writing a report.",
    )
    parser.add_argument(
        "--skip-missing",
        action="store_true",
        help="Validate each repo first and skip missing or inaccessible repos.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Process only the first N whitelisted usernames.",
    )
    return parser.parse_args()


def _entry(
    *,
    assignment: str,
    username: str,
    repo: str,
    status: str,
    github_http_status: int | None,
    message: str,
) -> dict:
    return {
        "assignment": assignment,
        "username": username,
        "repo": repo,
        "status": status,
        "github_http_status": github_http_status,
        "message": message,
    }


def batch_reinvite(
    assignment: str,
    dry_run: bool = False,
    skip_missing: bool = False,
    limit: int | None = None,
) -> dict:
    assignment_slug = get_assignment_slugs(assignment)[0]
    usernames = get_whitelisted_usernames(limit)
    entries = []

    for username in usernames:
        repo = repo_for(assignment_slug, username)

        if dry_run:
            entry = _entry(
                assignment=assignment_slug,
                username=username,
                repo=repo,
                status="dry_run",
                github_http_status=None,
                message="Dry run; collaborator endpoint was not called.",
            )
            entries.append(entry)
            append_audit_log(**entry)
            continue

        if skip_missing:
            repo_status = check_repo(repo)
            if repo_status["status"] == "missing":
                entry = _entry(
                    assignment=assignment_slug,
                    username=username,
                    repo=repo,
                    status="missing",
                    github_http_status=repo_status["github_http_status"],
                    message=repo_status["message"],
                )
                entries.append(entry)
                append_audit_log(**entry)
                continue
            if repo_status["status"] == "permission_issue":
                entry = _entry(
                    assignment=assignment_slug,
                    username=username,
                    repo=repo,
                    status="permission_issue",
                    github_http_status=repo_status["github_http_status"],
                    message=repo_status["message"],
                )
                entries.append(entry)
                append_audit_log(**entry)
                continue

        try:
            result = add_collaborator(repo, username)
            status = (
                "invitation_created"
                if result.github_http_status == 201
                else "already_had_access"
            )
            entry = _entry(
                assignment=assignment_slug,
                username=username,
                repo=repo,
                status=status,
                github_http_status=result.github_http_status,
                message=result.message,
            )
        except GitHubClientError as exc:
            status = "failure"
            if exc.github_http_status == 404:
                status = "missing"
            elif exc.github_http_status == 403:
                status = "permission_issue"
            entry = _entry(
                assignment=assignment_slug,
                username=username,
                repo=repo,
                status=status,
                github_http_status=exc.github_http_status,
                message=exc.message,
            )

        entries.append(entry)
        append_audit_log(**entry)

    counts = Counter(entry["status"] for entry in entries)
    summary = {
        "assignment": assignment_slug,
        "total_attempted": len(entries),
        "successes": counts.get("invitation_created", 0)
        + counts.get("already_had_access", 0),
        "invitation_created": counts.get("invitation_created", 0),
        "already_had_access": counts.get("already_had_access", 0),
        "missing_repos": counts.get("missing", 0),
        "permission_issues": counts.get("permission_issue", 0),
        "failures": counts.get("failure", 0),
        "dry_run": dry_run,
    }
    report = build_report(entries, summary)

    if not dry_run:
        save_report(REPORTS_DIR / "batch_reinvite_report.json", report)

    return report


def print_summary(report: dict) -> None:
    summary = report["summary"]
    print(f"Total attempted: {summary['total_attempted']}")
    print(f"Successes: {summary['successes']}")
    print(f"Already had access: {summary['already_had_access']}")
    print(f"Missing repos: {summary['missing_repos']}")
    print(f"Permission issues: {summary['permission_issues']}")
    print(f"Failures: {summary['failures']}")
    if summary["dry_run"]:
        print("Dry run: no GitHub changes were made and no report was written.")
    else:
        print("Saved report to reports/batch_reinvite_report.json.")


def main() -> None:
    args = parse_args()
    try:
        report = batch_reinvite(
            args.assignment,
            dry_run=args.dry_run,
            skip_missing=args.skip_missing,
            limit=args.limit,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc

    print_summary(report)


if __name__ == "__main__":
    main()
