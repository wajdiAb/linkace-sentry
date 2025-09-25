import asyncio
import os
import logging
from dotenv import load_dotenv
from src.services.link_monitor import LinkMonitoringService

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    # Get configuration from environment
    linkace_url = os.getenv('LINKACE_BASE_URL', 'http://localhost:8080')
    api_key = os.getenv('LINKACE_API_TOKEN')
    # Convert check interval from minutes to seconds
    check_interval = int(os.getenv('CHECK_INTERVAL_MIN', '60')) * 60
    concurrency = int(os.getenv('CONCURRENCY', '10'))
    timeout = int(os.getenv('CHECK_TIMEOUT', '30'))
    
    # AWS configuration
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    sns_topic_arn = os.getenv('AWS_SNS_TOPIC_ARN')
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

    if not api_key:
        raise ValueError("LINKACE_API_TOKEN environment variable must be set")
    if not sns_topic_arn:
        raise ValueError("AWS_SNS_TOPIC_ARN environment variable must be set")
    # if not aws_access_key or not aws_secret_key:
    #     raise ValueError("AWS credentials must be set")

    logger.info("Starting LinkAce monitoring service")
    logger.info("LinkAce URL: %s", linkace_url)
    logger.info("Check interval: %d seconds", check_interval)
    logger.info("Concurrency: %d", concurrency)

    service = LinkMonitoringService(
        linkace_url=linkace_url,
        api_key=api_key,
        sns_topic_arn=sns_topic_arn,
        aws_region=aws_region,
        check_interval=check_interval,
        concurrency=concurrency,
        timeout=timeout
    )

    try:
        await service.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping service...")
        service.stop()
    except Exception as e:
        logger.error("Fatal error: %s", str(e))
        raise

    # Example of a dead link report
    dead_link_report = {
        "type": "dead_link",
        "link": {
            "id": 123,
            "url": "https://example.com",
            "title": "Example Site",
            "last_checked": "2025-09-22T10:00:00Z"
        },
        "check_result": {
            "error": "Connection refused",
            "status_code": None,
            "response_time": 0
        }
    }
    logger.info("Dead link report: %s", dead_link_report)

if __name__ == "__main__":
    asyncio.run(main())