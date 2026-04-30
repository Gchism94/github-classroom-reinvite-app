import json
import re
from pathlib import Path

USERNAME_RE = re.compile(r"^[a-zA-Z0-9-]{1,39}$")
DATA_DIR = Path("data")


def normalize_username(username: str) -> str:
    return username.strip().lower()


def is_valid_github_username(username: str) -> bool:
    username = normalize_username(username)
    if not USERNAME_RE.match(username):
        return False
    if username.startswith("-") or username.endswith("-"):
        return False
    if "--" in username:
        return False
    return True


def load_whitelist() -> set[str]:
    path = DATA_DIR / "whitelist.json"
    with path.open() as f:
        return {normalize_username(u) for u in json.load(f)}


def is_authorized(username: str) -> bool:
    username = normalize_username(username)
    return username in load_whitelist()
