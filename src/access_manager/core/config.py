from pydantic import PostgresDsn
from pydantic_settings import BaseSettings # Используйте pydantic_settings для Pydantic v2+

class Settings(BaseSettings):
    postgres_dsn: PostgresDsn
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:

        pass

settings = Settings()