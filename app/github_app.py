from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
import requests

from app.config import ConfigurationError, Settings, get_settings

GITHUB_API_BASE = "https://api.github.com"
_cached_token: str | None = None
_cached_expires_at: datetime | None = None


class GitHubAppAuthError(RuntimeError):
    pass


def create_jwt(settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    settings.validate_github_app_config()
    now = datetime.now(timezone.utc)
    payload = {
        "iat": int((now - timedelta(seconds=60)).timestamp()),
        "exp": int((now + timedelta(minutes=9)).timestamp()),
        "iss": settings.github_app_id,
    }
    return jwt.encode(payload, settings.private_key, algorithm="RS256")


def get_installation_token(settings: Settings | None = None) -> str:
    global _cached_expires_at, _cached_token

    if (
        _cached_token
        and _cached_expires_at
        and _cached_expires_at > datetime.now(timezone.utc) + timedelta(minutes=5)
    ):
        return _cached_token

    settings = settings or get_settings()
    try:
        app_jwt = create_jwt(settings)
    except ConfigurationError:
        raise
    except Exception as exc:
        raise GitHubAppAuthError("Unable to create GitHub App JWT.") from exc

    url = (
        f"{GITHUB_API_BASE}/app/installations/"
        f"{settings.github_installation_id}/access_tokens"
    )
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    try:
        response = requests.post(url, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise GitHubAppAuthError("Unable to get a GitHub installation token.") from exc
    except ValueError as exc:
        raise GitHubAppAuthError("GitHub returned an invalid token response.") from exc

    token = data.get("token")
    expires_at = data.get("expires_at")
    if not token:
        raise GitHubAppAuthError("GitHub token response did not include a token.")

    _cached_token = token
    if expires_at:
        _cached_expires_at = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    else:
        _cached_expires_at = datetime.now(timezone.utc) + timedelta(minutes=55)

    return token
