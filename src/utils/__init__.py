"""Python dotenv file loader."""
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import os

def load_env(env_file: Optional[Path] = None) -> None:
    """Load environment variables from .env file."""
    if env_file is None:
        env_file = Path(__file__).parent.parent / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)