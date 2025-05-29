from typing import Optional

from pydantic import PostgresDsn
from pydantic_settings import (  # Используйте pydantic_settings для Pydantic v2+
    BaseSettings,
)


class Settings(BaseSettings):
    postgres_dsn: PostgresDsn
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    test_postgres_dsn: Optional[PostgresDsn] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
