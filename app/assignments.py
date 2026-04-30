import json
from pathlib import Path

DATA_DIR = Path("data")


def load_assignments() -> list[str]:
    path = DATA_DIR / "assignments.json"
    with path.open() as f:
        return json.load(f)


def is_valid_assignment(assignment: str) -> bool:
    return assignment in load_assignments()


def build_repo_name(assignment: str, username: str) -> str:
    return f"{assignment}-{username}"
