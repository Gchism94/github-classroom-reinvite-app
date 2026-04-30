import requests
from app.config import get_settings
from app.github_app_auth import get_installation_access_token

GITHUB_API_BASE = "https://api.github.com"


class GitHubClientError(Exception):
    def __init__(self, status_code: int, detail: dict | str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(str(detail))


def add_collaborator_with_write_access(repo: str, username: str) -> dict:
    settings = get_settings()
    token = get_installation_access_token()

    url = f"{GITHUB_API_BASE}/repos/{settings.github_org}/{repo}/collaborators/{username}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"permission": "push"}

    response = requests.put(url, headers=headers, json=payload, timeout=20)

    if response.status_code in (201, 204):
        return {
            "repo": repo,
            "username": username,
            "status_code": response.status_code,
        }

    try:
        detail = response.json()
    except ValueError:
        detail = response.text

    raise GitHubClientError(response.status_code, detail)
