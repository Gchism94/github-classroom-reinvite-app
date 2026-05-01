from __future__ import annotations

import json
from typing import Any

from app.config import DATA_DIR


def _normalize_assignment_record(assignment: Any) -> dict[str, Any] | None:
    if isinstance(assignment, str) and assignment.strip():
        slug = assignment.strip()
        return {
            "id": None,
            "title": slug,
            "slug": slug,
            "invite_link": None,
            "deadline": None,
        }

    if not isinstance(assignment, dict):
        return None

    slug = assignment.get("slug")
    if not isinstance(slug, str) or not slug.strip():
        return None

    title = assignment.get("title")
    return {
        "id": assignment.get("id"),
        "title": title if isinstance(title, str) and title.strip() else slug.strip(),
        "slug": slug.strip(),
        "invite_link": assignment.get("invite_link"),
        "type": assignment.get("type"),
        "deadline": assignment.get("deadline"),
        "accepted": assignment.get("accepted"),
        "submitted": assignment.get("submitted"),
        "passing": assignment.get("passing"),
    }


def load_assignments() -> list[str]:
    return [assignment["slug"] for assignment in load_assignment_records()]


def load_assignment_records() -> list[dict[str, Any]]:
    path = DATA_DIR / "assignments.json"
    if not path.exists():
        path = DATA_DIR / "assignments.example.json"
    with path.open() as f:
        assignments = json.load(f)

    if not isinstance(assignments, list):
        raise ValueError("Assignment data must be a JSON list.")

    normalized = [
        record
        for record in (_normalize_assignment_record(assignment) for assignment in assignments)
        if record is not None
    ]
    return normalized


def is_valid_assignment(assignment: str) -> bool:
    return assignment in load_assignments()


def build_repo_name(assignment: str, username: str) -> str:
    return f"{assignment}-{username}"
