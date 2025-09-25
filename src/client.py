"""LinkAce API client."""
import httpx
from typing import Dict, Any, Optional

class LinkAceClient:
    """Client for interacting with LinkAce API."""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        """Initialize the client.
        
        Args:
            base_url: The base URL of the LinkAce instance
            api_key: The API token for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def get_links_page(self, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Get a page of links.
        
        Args:
            page: Page number to retrieve
            per_page: Number of items per page
            
        Returns:
            JSON response from the API
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/api/v1/links",
                params={"page": page, "per_page": per_page},
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def update_link_status(
        self,
        link_id: int,
        is_working: bool,
        status_code: Optional[int] = None,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a link's status.
        
        Args:
            link_id: ID of the link to update
            is_working: Whether the link is working
            status_code: HTTP status code from checking the link
            error: Error message if the link check failed
            
        Returns:
            JSON response from the API
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            data = {
                "status": 0 if not is_working else 1,  # 0 = offline, 1 = online
            }
            if status_code is not None:
                data["status_code"] = status_code
            if error is not None:
                data["error"] = error
                
            response = await client.put(
                f"{self.base_url}/api/v1/links/{link_id}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()
            
    async def create_link(
        self,
        url: str,
        title: str,
        tags: list[str],
        check_disabled: bool = False,
        status: int = 1
    ) -> Dict[str, Any]:
        """Create a new link.
        
        Args:
            url: The URL to add
            title: Link title
            tags: List of tags
            check_disabled: Whether link checking is disabled
            status: Link status (0=offline, 1=online)
            
        Returns:
            JSON response from the API
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            data = {
                "url": url,
                "title": title,
                "tags": tags,
                "check_disabled": check_disabled,
                "status": status
            }
                
            response = await client.post(
                f"{self.base_url}/api/v1/links",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()

    async def update_link(
        self,
        link_id: int,
        status: int | None = None,
        tags: list[str] | None = None,
        check_disabled: bool | None = None,
        error: str | None = None
    ) -> Dict[str, Any]:
        """Update a link's fields.
        
        Args:
            link_id: ID of the link to update
            status: Link status (0=offline, 1=online)
            tags: List of tags
            check_disabled: Whether link checking is disabled
            error: Error message if the link is broken
            
        Returns:
            JSON response from the API
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            data = {}
            if status is not None:
                data["status"] = status
            if tags is not None:
                data["tags"] = tags
            if check_disabled is not None:
                data["check_disabled"] = check_disabled
            if error is not None:
                data["error"] = error
                
            response = await client.put(
                f"{self.base_url}/api/v1/links/{link_id}",
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            return response.json()