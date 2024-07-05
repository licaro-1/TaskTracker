import os
from pathlib import Path

from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent

STATIC_URL = "static/"

STATIC_USER_IMAGES_URL = STATIC_URL + "user_images/"

STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL)

STATIC_USER_IMAGES_ROOT = os.path.join(BASE_DIR, STATIC_USER_IMAGES_URL)


class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000


class AuthConfig(BaseModel):
    private_key_patch: Path = BASE_DIR / "core" / "authentication" / "certs" / "jwt-private.pem"
    public_key_patch: Path = BASE_DIR / "core" / "authentication" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_min: int = 3600
    token_type: str = "Bearer"


class DatabaseConfig(BaseModel):
    url: PostgresDsn
    echo: bool = False
    pool_size: int = 50
    max_overflow: int = 10


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"
    auth: str = "/auth"
    users: str = "/users"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class Settings(BaseSettings):
    """
    General settings of project backend.
    """
    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__"
    )
    api: ApiPrefix = ApiPrefix()
    auth: AuthConfig
    run: RunConfig = RunConfig()
    db: DatabaseConfig


settings = Settings()
