"""Main entry point for LinkAce Sentry service."""

import asyncio
import logging
import signal
import sys
from src.service import LinkAceSentry
from src.utils import load_env
import os

# Load environment variables
load_env()

# Debug: print settings
print("LINKACE_BASE_URL:", os.getenv("LINKACE_BASE_URL"))
print("LINKACE_API_TOKEN:", os.getenv("LINKACE_API_TOKEN"))
print("AWS_SNS_TOPIC_ARN:", os.getenv("AWS_SNS_TOPIC_ARN"))
print("CHECK_INTERVAL_MIN:", os.getenv("CHECK_INTERVAL_MIN", "30"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global variable to control service shutdown
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

async def main():
    """Run the LinkAce Sentry service."""
    logger.info("Starting LinkAce Sentry service...")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    service = LinkAceSentry()
    try:
        await service.start()
        logger.info("Service started successfully, scheduler is running...")
        
        # Keep the service running until shutdown signal
        while not shutdown_event.is_set():
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=60)
            except asyncio.TimeoutError:
                # Timeout is expected, continue running
                logger.debug("Service heartbeat: still running...")
                continue
            
        logger.info("Shutdown event received, stopping service...")
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Service error: {e}", exc_info=True)
        raise
    finally:
        await service.stop()
        logger.info("Service stopped successfully")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Service interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)