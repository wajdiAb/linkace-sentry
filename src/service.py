"""Main service logic for LinkAce Sentry."""

import asyncio
import logging
from datetime import datetime
from typing import List, Set
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import settings
from .services.linkace_client import LinkAceClient
from .services.notification_service import NotificationService
from .checker import URLChecker
from .cache import Cache
from .models import Bookmark, CheckResult

logger = logging.getLogger(__name__)


class LinkAceSentry:
    """Main service for checking and updating bookmarks."""
    
    def __init__(self):
        self.api = LinkAceClient(settings.LINKACE_BASE_URL, settings.LINKACE_API_TOKEN)
        self.checker = URLChecker()
        self.cache = Cache()
        self.scheduler = AsyncIOScheduler()
        self.semaphore = asyncio.Semaphore(settings.CONCURRENCY)
        self.notifier = NotificationService(settings.AWS_SNS_TOPIC_ARN, settings.AWS_REGION)
    
    async def start(self):
        """Start the service."""
        # Setup scheduled job
        self.scheduler.add_job(
            self.run_once,
            trigger=IntervalTrigger(minutes=settings.CHECK_INTERVAL_MIN),
            id="check_bookmarks",
            replace_existing=True,
            max_instances=1
        )
        self.scheduler.start()
        
        logger.info(f"Service started, checking every {settings.CHECK_INTERVAL_MIN} minutes")
        
        # Run initial check
        await self.run_once()
    
    async def stop(self):
        """Stop the service."""
        self.scheduler.shutdown()
        logger.info("Service stopped")
    
    async def run_once(self):
        """Run one complete check cycle."""
        logger.info("Starting bookmark check cycle")
        start_time = datetime.now()
        
        try:
            page = 1
            total_processed = 0
            
            while True:
                # Get batch of bookmarks
                logger.info(f"Fetching bookmarks page {page}...")
                response = await self.api.list_bookmarks(page)
                logger.info(f"API Response: {response}")
                
                bookmarks = []
                for data in response.get('data', []):
                    bookmarks.append(Bookmark(
                        id=str(data['id']),
                        url=data['url'],
                        title=data.get('title', ''),
                        tags=[]  # We'll update this if needed
                    ))
                logger.info(f"Found {len(bookmarks)} bookmarks on page {page}")
                if not bookmarks:
                    break
                
                # Process bookmarks concurrently
                tasks = [self._process_bookmark(bookmark) for bookmark in bookmarks]
                logger.info(f"Processing {len(tasks)} bookmarks concurrently...")
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Log any errors
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        logger.error(f"Error processing bookmark {bookmarks[i].id}: {result}")
                
                total_processed += len(bookmarks)
                
                # Check if there are more pages
                meta = response.get('meta', {})
                current_page = meta.get('current_page', 0)
                last_page = meta.get('last_page', 0)
                
                if current_page >= last_page:
                    break
                    
                page += 1
            
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"Check cycle completed",
                extra={
                    "total_processed": total_processed,
                    "duration_seconds": round(duration, 2)
                }
            )
            
        except Exception as e:
            logger.error(f"Check cycle failed: {e}")
            raise
    
    async def _process_bookmark(self, bookmark: Bookmark):
        """Process a single bookmark."""
        async with self.semaphore:
            start_time = datetime.now()
            
            try:
                # Check URL
                logger.info(f"Checking URL: {bookmark.url}")
                result = await self.checker.check_url(bookmark.url)
                logger.info(f"Check result for {bookmark.url}: {result}")
                
                # Update cache
                status = "dead" if not result.is_alive else "alive"
                logger.info(f"Setting status for bookmark {bookmark.id} to {status}")
                self.cache.update_status(
                    bookmark.id,
                    status,
                    result.final_url
                )
                
                # Determine needed actions
                actions = self._determine_actions(bookmark, result)
                
                # Apply actions
                if actions:
                    await self._apply_actions(bookmark, list(actions))
                
                # Convert bookmark data to dict (used for both types of notifications)
                link_data = {
                    "id": bookmark.id,
                    "url": bookmark.url,
                    "title": getattr(bookmark, 'title', ''),
                    "last_checked_at": datetime.now().isoformat()
                }
                
                # Convert result to dict (used for both types of notifications)
                check_result = {
                    "error": str(result.error) if result.error else None,
                    "status_code": result.status_code if hasattr(result, 'status_code') else None,
                    "response_time": 0,  # We'll add this feature later
                    "final_url": result.final_url if hasattr(result, 'final_url') else None
                }

                # Send appropriate notification based on link status
                if "add_dead" in actions:
                    logger.info(f"Link {bookmark.url} is dead, sending notification...")
                    await self.notifier.notify_dead_link(link_data, check_result)
                    logger.info("Dead link notification sent successfully!")
                elif result.is_alive:
                    logger.info(f"Link {bookmark.url} is working, sending notification...")
                    await self.notifier.notify_working_link(link_data, check_result)
                    logger.info("Working link notification sent successfully!")
                
                duration = (datetime.now() - start_time).total_seconds()
                logger.info(
                    f"Processed bookmark {bookmark.id} ({bookmark.url}) in {round(duration, 2)}s with actions: {', '.join(actions)}"
                )
                
            except Exception as e:
                logger.error(
                    f"Failed to process bookmark {bookmark.id} ({bookmark.url}): {str(e)}"
                )
    
    def _determine_actions(self, bookmark: Bookmark, result: CheckResult) -> Set[str]:
        """Determine what actions to take based on check result."""
        actions = set()
        current_tags = set(bookmark.tags)
        
        # Handle dead status
        if not result.is_alive:
            if self.cache.should_mark_dead(bookmark.id):
                if settings.TAG_DEAD_NAME not in current_tags:
                        actions.add("add_dead")
        else:
            if settings.TAG_DEAD_NAME in current_tags:
                actions.add("remove_dead")
        
        # Handle redirects
        if result.redirected and settings.TAG_REDIRECTED_NAME:
            if settings.TAG_REDIRECTED_NAME not in current_tags:
                actions.add("add_redirected")
        
        return actions
    
    async def _apply_actions(self, bookmark: Bookmark, actions: Set[str]):
        """Apply actions to a bookmark."""
        current_tags = set(bookmark.tags)
        
        for action in actions:
            if action == "add_dead":
                if settings.UPDATE_MODE == "tags":
                    current_tags.add(settings.TAG_DEAD_NAME)
                else:
                    await self.api.update_bookmark_note_prefix_dead(bookmark.id, True)
            
            elif action == "remove_dead":
                if settings.UPDATE_MODE == "tags":
                    current_tags.discard(settings.TAG_DEAD_NAME)
                else:
                    await self.api.update_bookmark_note_prefix_dead(bookmark.id, False)
            
            elif action == "add_redirected" and settings.UPDATE_MODE == "tags":
                current_tags.add(settings.TAG_REDIRECTED_NAME)
        
        # Update tags if needed
        if settings.UPDATE_MODE == "tags" and current_tags != set(bookmark.tags):
            await self.api.update_bookmark_tags(bookmark.id, list(current_tags))