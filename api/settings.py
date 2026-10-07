from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str = "postgresql+psycopg://app_user:password@db:5432/app_db"

    # Auth.
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_consumer_key: str = "streamforge"
    access_token_ttl_minutes: int = 15


settings = Settings()
