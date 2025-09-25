from typing import List, Dict, Any
import httpx
import asyncio
from datetime import datetime
from urllib.parse import urlparse

class LinkChecker:
    def __init__(self, concurrency: int = 10, timeout: int = 30):
        """
        Initialize the link checker service.
        
        Args:
            concurrency: Maximum number of concurrent URL checks
            timeout: Timeout in seconds for each URL check
        """
        self.concurrency = concurrency
        self.timeout = timeout
        self._semaphore = asyncio.Semaphore(concurrency)
    
    async def check_url(self, url: str) -> Dict[str, Any]:
        """
        Check a single URL and return its status.
        
        Args:
            url: The URL to check
            
        Returns:
            Dict containing:
                - status: 0 for dead, 1 for alive
                - error: Error message if any
                - status_code: HTTP status code if received
                - response_time: Time taken for the request in seconds
        """
        try:
            # Basic URL validation
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return {
                    "status": 0,
                    "error": "Invalid URL format",
                    "status_code": None,
                    "response_time": 0
                }

            async with self._semaphore:
                start_time = datetime.now()
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        url,
                        timeout=self.timeout,
                        follow_redirects=True
                    )
                    
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()

                # Consider 2xx and 3xx as success
                is_success = 200 <= response.status_code < 400
                
                return {
                    "status": 1 if is_success else 0,
                    "error": None if is_success else f"HTTP {response.status_code}",
                    "status_code": response.status_code,
                    "response_time": response_time
                }

        except httpx.TimeoutException:
            return {
                "status": 0,
                "error": "Request timed out",
                "status_code": None,
                "response_time": self.timeout
            }
        except httpx.RequestError as e:
            return {
                "status": 0,
                "error": str(e),
                "status_code": None,
                "response_time": 0
            }
        except Exception as e:
            return {
                "status": 0,
                "error": f"Unexpected error: {str(e)}",
                "status_code": None,
                "response_time": 0
            }

    async def check_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Check multiple URLs concurrently.
        
        Args:
            urls: List of URLs to check
            
        Returns:
            List of status dictionaries, one per URL
        """
        tasks = [self.check_url(url) for url in urls]
        return await asyncio.gather(*tasks)