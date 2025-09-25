"""Utility functions for LinkAce Sentry."""

import os
from pathlib import Path
from dotenv import load_dotenv

def load_env(env_path: Path | str | None = None):
    """Load environment variables from .env file.
    
    Args:
        env_path: Optional path to .env file. If not provided, looks in parent directory.
    """
    if env_path is None:
        env_path = Path(__file__).parent.parent / '.env'
        
    load_dotenv(dotenv_path=env_path)
    
    # Set defaults for optional variables
    if not os.getenv('REQUEST_TIMEOUT'):
        os.environ['REQUEST_TIMEOUT'] = '30'
    if not os.getenv('CONCURRENCY'):
        os.environ['CONCURRENCY'] = '5'
    if not os.getenv('AWS_SNS_TOPIC_ARN'):
        os.environ['AWS_SNS_TOPIC_ARN'] = ''
    
    # Set default values for optional variables
    if not os.getenv('REQUEST_TIMEOUT'):
        os.environ['REQUEST_TIMEOUT'] = '30'
    if not os.getenv('CONCURRENCY'):
        os.environ['CONCURRENCY'] = '5'
    if not os.getenv('AWS_SNS_TOPIC_ARN'):
        os.environ['AWS_SNS_TOPIC_ARN'] = ''  # Empty by default