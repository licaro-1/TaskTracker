import os
from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent

STATIC_URL = "static/"

STATIC_USER_IMAGES_URL = STATIC_URL + "user_images/"

STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL)

STATIC_USER_IMAGES_ROOT = os.path.join(BASE_DIR, STATIC_USER_IMAGES_URL)

USER_IMAGES_URL = BASE_DIR / STATIC_URL / "user_images"


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class AuthConfig(BaseModel):
    private_key_patch: Path = BASE_DIR / "authentication" / "certs" / "jwt-private.pem"
    public_key_patch: Path = BASE_DIR / "authentication" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_min: int = 7200
    refresh_token_expire_days: int = 30
    token_type: str = "Bearer"


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class PytestDatabaseConfig(BaseModel):
    url: str = "sqlite+aiosqlite:///tests/test.db"


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"
    tasks: str = "/tasks"
    task_statuses: str = "/task-statuses"
    task_comments: str = "/task-comments"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class SmtpEmail(BaseModel):
    user: str
    password: str
    host: str = "smtp.gmail.com"
    port: int = 465
    broker_url: str


class Settings(BaseSettings):
    """
    General settings of project backend.
    """

    model_config = SettingsConfigDict(
        env_file=(
            f"{BASE_DIR}/.env-n-dev",
            f"{BASE_DIR}/.env",
        ),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    api: ApiPrefix = ApiPrefix()
    auth: AuthConfig = AuthConfig()
    run: RunConfig = RunConfig()
    db: DatabaseConfig
    pytest_db: PytestDatabaseConfig = PytestDatabaseConfig()
    smtp: SmtpEmail


settings = Settings()
