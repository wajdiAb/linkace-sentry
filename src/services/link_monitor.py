import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from src.services.linkace_client import LinkAceClient
from src.services.link_checker import LinkChecker
from src.services.notification_service import NotificationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LinkMonitoringService:
    def __init__(
        self,
        linkace_url: str,
        api_key: str,
        sns_topic_arn: str,
        aws_region: str = 'us-east-1',
        check_interval: int = 3600,  # Default to 1 hour
        concurrency: int = 10,
        timeout: int = 30
    ):
        self.check_interval = check_interval
        self.linkace = LinkAceClient(linkace_url, api_key)
        self.checker = LinkChecker(concurrency=concurrency, timeout=timeout)
        self.notifier = NotificationService(sns_topic_arn, aws_region)
        self._running = False
    
    async def check_and_update_links(self, page: int = 1, per_page: int = 25) -> None:
        """
        Fetch a page of links, check their status, and update any dead links.
        """
        try:
            # Get links from LinkAce
            response = await self.linkace.list_bookmarks(page=page, per_page=per_page)
            if not response.get('data'):
                logger.info("No links found on page %d", page)
                return

            links = response['data']
            urls_to_check = []
            link_map = {}  # Map URLs to their LinkAce IDs

            # Filter links that need checking
            for link in links:
                # Skip links where check is disabled
                if link.get('check_disabled', False):
                    logger.debug("Skipping link %s - checking disabled", link['url'])
                    continue
                
                # Skip links checked recently (within last hour)
                last_checked = link.get('last_checked_at')
                if last_checked:
                    last_checked = datetime.fromisoformat(last_checked.replace('Z', '+00:00'))
                    if datetime.now() - last_checked < timedelta(hours=1):
                        logger.debug("Skipping link %s - checked recently", link['url'])
                        continue

                urls_to_check.append(link['url'])
                link_map[link['url']] = link['id']

            if not urls_to_check:
                logger.info("No links need checking on page %d", page)
                return

            # Check URLs in parallel
            logger.info("Checking %d URLs...", len(urls_to_check))
            logger.info("URLs to check: %s", urls_to_check)
            results = await self.checker.check_urls(urls_to_check)

            # Process results
            logger.info("Check results: %s", results)
            for url, result in zip(urls_to_check, results):
                link_id = link_map[url]
                if result['status'] == 0:  # Dead link
                    logger.warning("Dead link found: %s (Error: %s)", url, result['error'])
                    try:
                        await self.linkace.update_link(
                            link_id=link_id,
                            status=0,  # Mark as dead
                            tags=['dead']
                        )
                        logger.info("Updated link %s as dead", url)
                        
                        # Send notification about dead link
                        await self.notifier.notify_dead_link(
                            link_data=next(link for link in links if link['id'] == link_id),
                            check_result=result
                        )
                    except Exception as e:
                        logger.error("Failed to update link %s: %s", url, str(e))

        except Exception as e:
            logger.error("Error checking links on page %d: %s", page, str(e))

    async def run(self) -> None:
        """
        Main service loop. Continuously monitors links at the specified interval.
        """
        self._running = True
        while self._running:
            try:
                logger.info("Starting link check cycle...")
                page = 1
                while True:
                    response = await self.linkace.list_bookmarks(page=page)
                    if not response.get('data'):
                        break
                    
                    await self.check_and_update_links(page=page)
                    
                    # Check if there are more pages
                    if not response.get('next_page_url'):
                        break
                    page += 1

                logger.info("Link check cycle completed. Waiting %d seconds...", self.check_interval)
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error("Error in monitoring cycle: %s", str(e))
                logger.info("Retrying in 60 seconds...")
                await asyncio.sleep(60)

    def stop(self) -> None:
        """Stop the monitoring service."""
        self._running = False