from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime configuration. Values come from env vars (`.env` in dev, Railway in prod)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development")
    site_url: str = Field(default="http://localhost:8000")

    # Railway-injected build metadata. Falls back to "dev" / "local" locally.
    railway_git_commit_sha: str = Field(default="dev", alias="RAILWAY_GIT_COMMIT_SHA")
    railway_deployment_id: str = Field(default="local", alias="RAILWAY_DEPLOYMENT_ID")

    # Contact form SMTP. If smtp_host is empty, contact submissions are
    # log-only (dev mode) and the form returns success without sending.
    smtp_host: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    contact_email_to: str = Field(default="align@qoat.ai")
    contact_email_from: str = Field(default="")  # falls back to smtp_user

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def commit_short(self) -> str:
        return self.railway_git_commit_sha[:7] if self.railway_git_commit_sha else "dev"

    @property
    def site_url_clean(self) -> str:
        return self.site_url.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
