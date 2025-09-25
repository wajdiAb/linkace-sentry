from typing import List, Dict, Any, Optional
import httpx
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LinkAceClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    async def create_link(self, url: str, title: str, tags: List[str] = None) -> Dict[str, Any]:
        """Create a new link in LinkAce"""
        link_data = {
            "url": url,
            "title": title,
            "tags": tags or []
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/links",
                headers=self.headers,
                json=link_data
            )
            response.raise_for_status()
            return response.json()

    async def delete_link(self, link_id: int) -> None:
        """Delete a link from LinkAce"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/api/v2/links/{link_id}",
                headers=self.headers
            )
            response.raise_for_status()

    async def list_bookmarks(self, page: int = 1, per_page: int = 25) -> Dict[str, Any]:
        """
        List all bookmarks with pagination.
        Returns the full API response including meta data.
        """
        logger.info(f"Requesting bookmarks from {self.base_url}/api/v2/links")
        logger.info(f"Using headers: {self.headers}")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v2/links",
                headers=self.headers,
                params={"page": page, "per_page": per_page},
                timeout=30.0  # Add a longer timeout
            )
            response.raise_for_status()
            return response.json()

    async def update_bookmark_tags(self, bookmark_id: str, tags: List[str]) -> Dict[str, Any]:
        """Update a bookmark's tags."""
        async with httpx.AsyncClient() as client:
            # First get current link data
            current = await client.get(
                f"{self.base_url}/api/v2/links/{bookmark_id}",
                headers=self.headers
            )
            current.raise_for_status()
            current_data = current.json()
            
            # Prepare update with all required fields
            update_data = {
                "url": current_data["url"],
                "title": current_data["title"],
                "tags": tags
            }
            
            response = await client.put(
                f"{self.base_url}/api/v2/links/{bookmark_id}",
                headers=self.headers,
                json=update_data
            )
            response.raise_for_status()
            return response.json()

    async def update_link(
        self,
        link_id: int,
        status: Optional[int] = None,
        check_disabled: Optional[bool] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Update a link's status, check_disabled flag, or tags."""
        async with httpx.AsyncClient() as client:
            # First get current link data
            current = await client.get(
                f"{self.base_url}/api/v2/links/{link_id}",
                headers=self.headers
            )
            current.raise_for_status()
            current_data = current.json()
            
            # Prepare update with all required fields
            update_data = {
                "url": current_data["url"],
                "title": current_data["title"],
                "tags": tags if tags is not None else current_data.get("tags", []),
                "check_disabled": check_disabled if check_disabled is not None else current_data.get("check_disabled", False),
                "status": status if status is not None else current_data.get("status", 1)
            }

            response = await client.put(
                f"{self.base_url}/api/v2/links/{link_id}",
                headers=self.headers,
                json=update_data
            )
            response.raise_for_status()
            return response.json()
                
    async def update_bookmark_note_prefix_dead(self, bookmark_id: str, is_dead: bool) -> Dict[str, Any]:
        """Update a bookmark's note to prefix it with [DEAD] if the link is dead."""
        async with httpx.AsyncClient() as client:
            # First get current note
            response = await client.get(
                f"{self.base_url}/api/v2/links/{bookmark_id}",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            current_note = data.get("description", "")
            
            # Add or remove [DEAD] prefix
            if is_dead and not current_note.startswith("[DEAD]"):
                new_note = f"[DEAD] {current_note}"
            elif not is_dead and current_note.startswith("[DEAD]"):
                new_note = current_note[6:].lstrip()  # Remove [DEAD] and any leading space
            else:
                new_note = current_note
            
            # Update the note
            response = await client.put(
                f"{self.base_url}/api/v2/links/{bookmark_id}",
                headers=self.headers,
                json={"description": new_note}
            )
            response.raise_for_status()
            return response.json()
            
    async def create_link(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new link in LinkAce.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v2/links",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()