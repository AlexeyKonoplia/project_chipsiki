from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/reviews"
    secret_key: str = "change-me-in-production-please-use-a-long-random-value"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    algorithm: str = "HS256"

    # Directory (inside container) where uploaded product images are stored.
    upload_dir: str = "/app/uploads"

    # These are stored as raw comma-separated strings (env: CORS_ORIGINS /
    # ADMIN_USERNAMES) and exposed as lists via the properties below. Keeping
    # them as `str` avoids pydantic-settings trying to JSON-decode the env var.
    cors_origins_raw: str = Field(
        "http://localhost:5173,http://localhost:8080,http://localhost",
        alias="CORS_ORIGINS",
    )
    # Usernames that are automatically granted admin rights.
    admin_usernames_raw: str = Field("koh0", alias="ADMIN_USERNAMES")

    @staticmethod
    def _split(value: str) -> list[str]:
        return [item.strip() for item in value.split(",") if item.strip()]

    @property
    def cors_origins(self) -> list[str]:
        return self._split(self.cors_origins_raw)

    @property
    def admin_usernames(self) -> list[str]:
        return self._split(self.admin_usernames_raw)


settings = Settings()
