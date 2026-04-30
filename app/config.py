from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class ConfigurationError(RuntimeError):
    pass


class Settings(BaseModel):
    github_app_id: str
    github_installation_id: str
    github_org: str
    github_private_key: Optional[str] = None
    github_classroom_id: Optional[str] = None
    github_classroom_token: Optional[str] = None

    @property
    def private_key(self) -> str:
        if self.github_private_key:
            return self.github_private_key.replace("\\n", "\n")

        raise ConfigurationError("Missing required environment variable: GITHUB_PRIVATE_KEY")

    def validate_github_app_config(self) -> None:
        missing = [
            name
            for name, value in (
                ("GITHUB_APP_ID", self.github_app_id),
                ("GITHUB_INSTALLATION_ID", self.github_installation_id),
                ("GITHUB_ORG", self.github_org),
                ("GITHUB_PRIVATE_KEY", self.github_private_key),
            )
            if not value
        ]
        if missing:
            raise ConfigurationError(
                "Missing required environment variable(s): " + ", ".join(missing)
            )


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        github_app_id=os.getenv("GITHUB_APP_ID", ""),
        github_installation_id=os.getenv("GITHUB_INSTALLATION_ID", ""),
        github_org=os.getenv("GITHUB_ORG", ""),
        github_private_key=os.getenv("GITHUB_PRIVATE_KEY"),
        github_classroom_id=os.getenv("GITHUB_CLASSROOM_ID"),
        github_classroom_token=os.getenv("GITHUB_CLASSROOM_TOKEN"),
    )
