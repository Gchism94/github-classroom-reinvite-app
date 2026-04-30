from __future__ import annotations

from dataclasses import dataclass

import requests

from app.config import get_settings
from app.github_app import get_installation_token

GITHUB_API_BASE = "https://api.github.com"


class GitHubClientError(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
        github_http_status: int | None = None,
    ):
        self.status_code = status_code
        self.message = message
        self.github_http_status = github_http_status
        super().__init__(message)


@dataclass(frozen=True)
class CollaboratorResult:
    message: str
    github_http_status: int


def add_collaborator(repo_name: str, username: str) -> CollaboratorResult:
    settings = get_settings()
    settings.validate_github_app_config()
    token = get_installation_token(settings)

    url = (
        f"{GITHUB_API_BASE}/repos/{settings.github_org}/"
        f"{repo_name}/collaborators/{username}"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    payload = {"permission": "push"}

    try:
        response = requests.put(url, headers=headers, json=payload, timeout=20)
    except requests.RequestException as exc:
        raise GitHubClientError(
            502,
            "GitHub could not be reached. Please try again later.",
            github_http_status=None,
        ) from exc

    if response.status_code == 201:
        return CollaboratorResult(
            message="Invitation created. Check your GitHub notifications or email.",
            github_http_status=response.status_code,
        )

    if response.status_code == 204:
        return CollaboratorResult(
            message="Write access is already active or has been restored.",
            github_http_status=response.status_code,
        )

    if response.status_code == 404:
        message = "Repository or user was not found for this assignment."
    elif response.status_code in (401, 403):
        message = "This tool is not authorized to update that repository."
    else:
        message = "GitHub could not complete the request. Please contact your instructor."

    raise GitHubClientError(
        response.status_code,
        message,
        github_http_status=response.status_code,
    )


def add_collaborator_with_write_access(repo: str, username: str) -> dict:
    result = add_collaborator(repo, username)
    return {"repo": repo, "username": username, "status": result.message}
