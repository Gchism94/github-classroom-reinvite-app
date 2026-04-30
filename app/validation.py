import re

USERNAME_RE = re.compile(r"^[a-zA-Z0-9-]{1,39}$")


def normalize_username(username: str) -> str:
    return username.strip().lower()


def is_valid_github_username(username: str) -> bool:
    username = normalize_username(username)
    if not USERNAME_RE.fullmatch(username):
        return False
    return not (username.startswith("-") or username.endswith("-"))
