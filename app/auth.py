from __future__ import annotations

import json
from pathlib import Path

from app.config import DATA_DIR
from app.validation import is_valid_github_username, normalize_username


def load_whitelist(path: Path | None = None) -> set[str]:
    path = path or DATA_DIR / "whitelist.json"
    with path.open() as f:
        usernames = json.load(f)

    if not isinstance(usernames, list):
        raise ValueError("Whitelist data must be a JSON list.")

    return {
        normalize_username(username)
        for username in usernames
        if isinstance(username, str) and username.strip()
    }


def is_authorized(username: str, whitelist: set[str] | None = None) -> bool:
    username = normalize_username(username)
    return username in (whitelist if whitelist is not None else load_whitelist())
