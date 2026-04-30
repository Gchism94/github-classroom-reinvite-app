from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import LOG_DIR

AUDIT_LOG_PATH = LOG_DIR / "audit.log"


def ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def append_audit_log(
    *,
    username: str,
    assignment: str,
    repo: str | None,
    status: str,
    github_http_status: int | None,
    message: str,
    path: Path | None = None,
) -> None:
    ensure_log_dir()
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "username": username,
        "assignment": assignment,
        "repo": repo,
        "status": status,
        "github_http_status": github_http_status,
        "message": message,
    }
    audit_path = path or AUDIT_LOG_PATH
    with audit_path.open("a") as log_file:
        log_file.write(json.dumps(entry, sort_keys=True) + "\n")
