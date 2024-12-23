import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Cluster Management API"
    API_V1_STR: str = "/api/v1"

    # Database configuration
    POSTGRES_SERVER: str = os.getenv("PGHOST", "localhost")
    POSTGRES_USER: str = os.getenv("PGUSER", "ansh")
    POSTGRES_PASSWORD: str = os.getenv("PGPASSWORD", "password")
    POSTGRES_DB: str = os.getenv("PGDATABASE", "test_db")
    POSTGRES_PORT: str = os.getenv("PGPORT", "5432")

    # Session configuration
    # app/core/config.py

    SECRET_KEY = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SECRET_KEY: str = "TODO_CHANGE_THIS_SECRET_KEY"  # TODO: Change in production
    SESSION_COOKIE_NAME: str = "this-session"
    SESSION_MAX_AGE: int = 1800  # 30 minutes in seconds

    # Database URL
    DATABASE_URL: str = os.getenv(
        "postgresql://ansh:password@localhost:5432/test_db",
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}",
    )


settings = Settings()
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
