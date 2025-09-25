from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    LINKACE_BASE_URL: str = "http://localhost:8080"
    LINKACE_API_TOKEN: str
    CHECK_INTERVAL_MIN: int = 30
    CONCURRENCY: int = 10
    TAG_DEAD_NAME: str = "dead"
    TAG_REDIRECTED_NAME: str = "redirected"
    UPDATE_MODE: str = "tags"
    ADMIN_TOKEN: str
    AWS_REGION: str = "eu-west-1"
    AWS_SNS_TOPIC_ARN: str
    request_timeout_s: int = 30  # Default timeout of 30 seconds
    max_redirects: int = 5  # Maximum number of redirects to follow
    cache_db_path: str = "cache.db"  # SQLite database file for caching

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()