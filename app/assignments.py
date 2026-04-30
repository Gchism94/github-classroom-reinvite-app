from __future__ import annotations

import json

from app.config import DATA_DIR


def load_assignments() -> list[str]:
    path = DATA_DIR / "assignments.json"
    with path.open() as f:
        assignments = json.load(f)

    if not isinstance(assignments, list):
        raise ValueError("Assignment data must be a JSON list.")

    return [
        assignment
        for assignment in assignments
        if isinstance(assignment, str) and assignment.strip()
    ]


def is_valid_assignment(assignment: str) -> bool:
    return assignment in load_assignments()


def build_repo_name(assignment: str, username: str) -> str:
    return f"{assignment}-{username}"
