from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests

from app.config import DATA_DIR, Settings, get_settings

GITHUB_API_BASE = "https://api.github.com"


class GitHubClassroomError(RuntimeError):
    pass


class GitHubClassroomClient:
    def __init__(self, token: str | None = None, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.token = token or self._resolve_token()

    def _resolve_token(self) -> str:
        if self.settings.github_classroom_token:
            return self.settings.github_classroom_token

        raise GitHubClassroomError(
            "GitHub Classroom sync requires GITHUB_CLASSROOM_TOKEN."
        )

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get_paginated(self, path: str) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        page = 1

        while True:
            response = requests.get(
                f"{GITHUB_API_BASE}{path}",
                headers=self.headers,
                params={"per_page": 100, "page": page},
                timeout=20,
            )
            if response.status_code != 200:
                raise GitHubClassroomError(
                    f"GitHub Classroom request failed with status {response.status_code}."
                )

            try:
                payload = response.json()
            except ValueError as exc:
                raise GitHubClassroomError(
                    "GitHub Classroom returned an invalid JSON response."
                ) from exc

            if isinstance(payload, dict):
                payload = [payload]
            if not isinstance(payload, list):
                raise GitHubClassroomError(
                    "GitHub Classroom returned an unexpected response shape."
                )

            results.extend(payload)
            if len(payload) < 100:
                break
            page += 1

        return results

    def list_classrooms(self) -> list[dict[str, Any]]:
        return self._get_paginated("/classrooms")

    def list_assignments(self, classroom_id: str | int) -> list[dict[str, Any]]:
        return self._get_paginated(f"/classrooms/{classroom_id}/assignments")

    def list_accepted_assignments(self, assignment_id: str | int) -> list[dict[str, Any]]:
        return self._get_paginated(f"/assignments/{assignment_id}/accepted_assignments")


def normalize_classroom_assignment(assignment: dict[str, Any]) -> dict[str, Any]:
    slug = assignment.get("slug")
    title = assignment.get("title")
    return {
        "id": assignment.get("id"),
        "title": title if isinstance(title, str) and title.strip() else slug,
        "slug": slug,
        "invite_link": assignment.get("invite_link"),
        "type": assignment.get("type"),
        "deadline": assignment.get("deadline"),
        "accepted": assignment.get("accepted"),
        "submitted": assignment.get("submitted"),
        "passing": assignment.get("passing"),
    }


def normalize_accepted_assignment(accepted: dict[str, Any]) -> dict[str, Any]:
    repository = accepted.get("repository") or {}
    students = accepted.get("students") or []
    return {
        "id": accepted.get("id"),
        "submitted": accepted.get("submitted"),
        "passing": accepted.get("passing"),
        "commit_count": accepted.get("commit_count"),
        "grade": accepted.get("grade"),
        "students": [
            {
                "id": student.get("id"),
                "login": student.get("login"),
                "html_url": student.get("html_url"),
            }
            for student in students
            if isinstance(student, dict)
        ],
        "repository": {
            "id": repository.get("id"),
            "full_name": repository.get("full_name"),
            "html_url": repository.get("html_url"),
            "private": repository.get("private"),
            "default_branch": repository.get("default_branch"),
        },
    }


def save_assignments(assignments: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "assignments.json"
    path.write_text(json_dumps(assignments))


def save_accepted_assignments(payload: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / "accepted_assignments.json"
    path.write_text(json_dumps(payload))


def build_accepted_assignments_payload(
    assignments: list[dict[str, Any]],
    accepted_by_assignment: dict[str, list[dict[str, Any]]],
    classroom_id: str,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for assignment in assignments:
        assignment_id = assignment["id"]
        assignment_slug = assignment["slug"]
        for accepted in accepted_by_assignment.get(str(assignment_id), []):
            repository = accepted.get("repository") or {}
            full_name = repository.get("full_name")
            repo_name = (
                full_name.rsplit("/", 1)[-1] if isinstance(full_name, str) else None
            )
            students = accepted.get("students") or []
            student_logins = [
                student.get("login")
                for student in students
                if isinstance(student, dict) and student.get("login")
            ]

            if not student_logins:
                records.append(
                    {
                        "assignment_id": assignment_id,
                        "assignment_slug": assignment_slug,
                        "github_username": None,
                        "repo_name": repo_name,
                        "repo_url": repository.get("html_url"),
                    }
                )
                continue

            for github_username in student_logins:
                records.append(
                    {
                        "assignment_id": assignment_id,
                        "assignment_slug": assignment_slug,
                        "github_username": github_username,
                        "repo_name": repo_name,
                        "repo_url": repository.get("html_url"),
                    }
                )

    return {
        "classroom_id": classroom_id,
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "accepted_assignments": records,
    }


def json_dumps(payload: Any) -> str:
    import json

    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
