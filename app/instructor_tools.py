from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from app.assignments import build_repo_name, load_assignments
from app.auth import load_whitelist
from app.config import BASE_DIR, get_settings
from app.github_app import get_installation_token

REPORTS_DIR = BASE_DIR / "reports"
GITHUB_API_BASE = "https://api.github.com"


def ensure_reports_dir() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def github_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_assignment_slugs(selected_assignment: str | None = None) -> list[str]:
    assignments = load_assignments()
    if selected_assignment is None:
        return assignments
    if selected_assignment not in assignments:
        raise ValueError(f"Invalid assignment: {selected_assignment}")
    return [selected_assignment]


def get_whitelisted_usernames(limit: int | None = None) -> list[str]:
    usernames = sorted(load_whitelist())
    if limit is not None:
        return usernames[:limit]
    return usernames


def check_repo(repo_name: str, token: str | None = None) -> dict[str, Any]:
    settings = get_settings()
    settings.validate_github_app_config()
    token = token or get_installation_token(settings)
    url = f"{GITHUB_API_BASE}/repos/{settings.github_org}/{repo_name}"

    try:
        response = requests.get(
            url,
            headers=github_headers(token),
            timeout=20,
        )
    except requests.RequestException:
        return {
            "repo": repo_name,
            "status": "failure",
            "github_http_status": None,
            "message": "GitHub could not be reached.",
        }

    if response.status_code == 200:
        return {
            "repo": repo_name,
            "status": "exists",
            "github_http_status": response.status_code,
            "message": "Repository exists.",
        }
    if response.status_code == 404:
        return {
            "repo": repo_name,
            "status": "missing",
            "github_http_status": response.status_code,
            "message": "Repository is missing or inaccessible.",
        }
    if response.status_code in (401, 403):
        return {
            "repo": repo_name,
            "status": "permission_issue",
            "github_http_status": response.status_code,
            "message": "GitHub App lacks access to this repository.",
        }
    return {
        "repo": repo_name,
        "status": "failure",
        "github_http_status": response.status_code,
        "message": "GitHub returned an unexpected status.",
    }


def build_report(entries: list[dict[str, Any]], summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "entries": entries,
    }


def save_report(path: Path, report: dict[str, Any]) -> None:
    ensure_reports_dir()
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


def repo_for(assignment_slug: str, username: str) -> str:
    return build_repo_name(assignment_slug, username)
