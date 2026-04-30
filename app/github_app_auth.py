from datetime import datetime, timedelta, timezone
import jwt
import requests
from app.config import get_settings

GITHUB_API_BASE = "https://api.github.com"


def create_app_jwt() -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)

    payload = {
        "iat": int((now - timedelta(seconds=60)).timestamp()),
        "exp": int((now + timedelta(minutes=9)).timestamp()),
        "iss": settings.github_app_id,
    }

    return jwt.encode(payload, settings.private_key, algorithm="RS256")


def get_installation_access_token() -> str:
    settings = get_settings()
    app_jwt = create_app_jwt()

    url = f"{GITHUB_API_BASE}/app/installations/{settings.github_installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {app_jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.post(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.json()["token"]
