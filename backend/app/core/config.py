from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_DEFAULT = "dev-secret-key-change-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://nigran:nigran360@localhost:5432/nigran360"
    # In production set SECRET_KEY to a strong random value (e.g. `openssl rand -hex 32`).
    # Startup is blocked if the insecure default is detected and ENVIRONMENT != "development".
    SECRET_KEY: str = _INSECURE_DEFAULT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    ENVIRONMENT: str = "development"

    @field_validator("SECRET_KEY")
    @classmethod
    def reject_insecure_secret_in_production(cls, v: str, info: object) -> str:
        import os
        env = os.getenv("ENVIRONMENT", "development")
        if v == _INSECURE_DEFAULT and env not in ("development", "test"):
            raise ValueError(
                "SECRET_KEY must be changed from the default before running in production. "
                "Set a strong random value via the SECRET_KEY environment variable."
            )
        return v


settings = Settings()
