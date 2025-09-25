"""LinkAce Sentry configuration."""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings."""
    
    # LinkAce API configuration
    linkace_base_url: str = os.getenv("LINKACE_BASE_URL", "http://localhost:8080")
    linkace_api_token: Optional[str] = os.getenv("LINKACE_API_TOKEN")
    
    # Checking behavior
    per_page: int = 100
    check_interval_min: int = 30
    concurrency: int = 10
    request_timeout_s: int = 8
    max_redirects: int = 5
    
    # Tag configuration
    tag_dead_name: str = "dead"
    tag_redirected_name: str = "redirected"
    
    # Cache configuration
    cache_db_path: str = "/data/cache.db"
    
    # Update mode: "tags" or "note"
    update_mode: str = "tags"
    
    # AWS SNS configuration for notifications
    aws_sns_topic_arn: Optional[str] = None  # Will be set via environment variable
    aws_region: str = "us-east-1"
    
    # Optional admin token for protected endpoints
    admin_token: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()