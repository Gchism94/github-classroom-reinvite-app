from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    github_app_id: str
    github_installation_id: str
    github_org: str
    github_private_key_path: str | None = None
    github_private_key: str | None = None
    app_secret_key: str = "change-me"

    @property
    def private_key(self) -> str:
        if self.github_private_key:
            return self.github_private_key.replace("\\n", "\n")

        if self.github_private_key_path:
            key_path = Path(self.github_private_key_path)
            if not key_path.exists():
                raise FileNotFoundError(
                    f"GitHub private key file not found: {self.github_private_key_path}"
                )
            return key_path.read_text()

        raise ValueError(
            "Missing GitHub private key. Set GITHUB_PRIVATE_KEY_PATH or GITHUB_PRIVATE_KEY."
        )


@lru_cache
def get_settings() -> Settings:
    return Settings(
        github_app_id=os.getenv("GITHUB_APP_ID", ""),
        github_installation_id=os.getenv("GITHUB_INSTALLATION_ID", ""),
        github_org=os.getenv("GITHUB_ORG", ""),
        github_private_key_path=os.getenv("GITHUB_PRIVATE_KEY_PATH"),
        github_private_key=os.getenv("GITHUB_PRIVATE_KEY"),
        app_secret_key=os.getenv("APP_SECRET_KEY", "change-me"),
    )
