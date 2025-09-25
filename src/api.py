"""LinkAce API client."""

import httpx
import logging
from typing import List, Tuple, Set, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings
from .models import Bookmark, Tag

logger = logging.getLogger(__name__)


class LinkAceAPI:
    """Client for interacting with LinkAce API."""
    
    def __init__(self):
        self.base_url = settings.linkace_base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {settings.linkace_api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def list_bookmarks(self, page: int = 1) -> Tuple[List[Bookmark], bool]:
        """List bookmarks with pagination."""
        async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/bookmarks",
                headers=self.headers,
                params={"page": page, "per_page": settings.per_page}
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Handle both {data: [...]} and raw list formats
            if isinstance(data, dict) and "data" in data:
                bookmarks_data = data["data"]
                has_next = data.get("next_page_url") is not None
            else:
                bookmarks_data = data
                has_next = len(bookmarks_data) == settings.per_page
            
            bookmarks = []
            for item in bookmarks_data:
                tags = []
                if "tags" in item:
                    for tag in item["tags"]:
                        if isinstance(tag, dict):
                            tags.append(tag["name"])
                        else:
                            tags.append(str(tag))
                
                bookmark = Bookmark(
                    id=str(item["id"]),
                    url=item["url"],
                    tags=tags,
                    title=item.get("title"),
                    note=item.get("note") or item.get("description")
                )
                bookmarks.append(bookmark)
            
            return bookmarks, has_next
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_bookmark(self, bookmark_id: str) -> Bookmark:
        """Get a single bookmark."""
        async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/bookmarks/{bookmark_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            data = response.json()
            tags = []
            if "tags" in data:
                for tag in data["tags"]:
                    if isinstance(tag, dict):
                        tags.append(tag["name"])
                    else:
                        tags.append(str(tag))
            
            return Bookmark(
                id=str(data["id"]),
                url=data["url"],
                tags=tags,
                title=data.get("title"),
                note=data.get("note") or data.get("description")
            )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def update_bookmark_tags(self, bookmark_id: str, tag_names: Set[str]) -> bool:
        """Update bookmark tags."""
        try:
            # Get current bookmark to preserve other fields
            bookmark = await self.get_bookmark(bookmark_id)
            
            async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
                response = await client.put(
                    f"{self.base_url}/api/v1/bookmarks/{bookmark_id}",
                    headers=self.headers,
                    json={
                        "url": bookmark.url,
                        "title": bookmark.title,
                        "note": bookmark.note,
                        "tags": list(tag_names)
                    }
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            logger.error(f"Failed to update tags for bookmark {bookmark_id}: {e}")
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def update_bookmark_note_prefix_dead(self, bookmark_id: str, add_dead: bool) -> bool:
        """Update bookmark note with [dead] prefix."""
        try:
            bookmark = await self.get_bookmark(bookmark_id)
            note = bookmark.note or ""
            
            if add_dead and not note.startswith("[dead]"):
                note = f"[dead] {note}".strip()
            elif not add_dead and note.startswith("[dead]"):
                note = note[6:].strip()
            
            async with httpx.AsyncClient(timeout=settings.request_timeout_s) as client:
                response = await client.put(
                    f"{self.base_url}/api/v1/bookmarks/{bookmark_id}",
                    headers=self.headers,
                    json={
                        "url": bookmark.url,
                        "title": bookmark.title,
                        "note": note,
                        "tags": bookmark.tags
                    }
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            logger.error(f"Failed to update note for bookmark {bookmark_id}: {e}")
            return False