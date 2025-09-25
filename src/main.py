"""Main entry point for LinkAce Sentry service."""

import asyncio
import logging
from src.service import LinkAceSentry
from src.utils import load_env
import os

# Load environment variables
load_env()

# Debug: print settings
print("LINKACE_BASE_URL:", os.getenv("LINKACE_BASE_URL"))
print("LINKACE_API_TOKEN:", os.getenv("LINKACE_API_TOKEN"))
print("AWS_SNS_TOPIC_ARN:", os.getenv("AWS_SNS_TOPIC_ARN"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Run the LinkAce Sentry service."""
    service = LinkAceSentry()
    try:
        await service.start()
        # Keep the service running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await service.stop()
    except Exception as e:
        logging.error(f"Service error: {e}", exc_info=True)
        await service.stop()
        raise

if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run(app, host=settings.host, port=settings.port)