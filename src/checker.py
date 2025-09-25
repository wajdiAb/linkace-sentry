"""URL checking service."""

import httpx
import logging
import asyncio
from urllib.parse import urlparse
from typing import Optional

from .config import settings
from .models import CheckResult

logger = logging.getLogger(__name__)


class URLChecker:
    """Service for checking URL status."""
    
    def __init__(self):
        self.timeout = settings.request_timeout_s
        self.max_redirects = settings.max_redirects
    
    async def check_url(self, url: str) -> CheckResult:
        """Check URL status with HEAD request, fallback to GET."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                follow_redirects=False  # Handle redirects manually
            ) as client:
                # Try HEAD first
                try:
                    response = await client.head(url)
                    if response.status_code in [403, 405, 501]:
                        # Fallback to GET for endpoints that don't support HEAD
                        response = await client.get(url)
                except httpx.HTTPError:
                    # Any HTTP error, try GET
                    response = await client.get(url)
                
                # Handle redirects
                if 300 <= response.status_code < 400:
                    return await self._handle_redirect(client, url, response)
                
                # Handle success/error
                if response.status_code >= 400:
                    return CheckResult(
                        is_alive=False,
                        status_code=response.status_code,
                        error=f"HTTP {response.status_code}"
                    )
                
                return CheckResult(
                    is_alive=True,
                    status_code=response.status_code,
                    final_url=str(response.url)
                )
                
        except httpx.TimeoutException:
            return CheckResult(
                is_alive=False,
                error="Request timeout"
            )
        except httpx.ConnectError as e:
            return CheckResult(
                is_alive=False,
                error=f"Connection error: {e}"
            )
        except Exception as e:
            return CheckResult(
                is_alive=False,
                error=str(e)
            )
    
    async def _handle_redirect(
        self, 
        client: httpx.AsyncClient,
        original_url: str,
        response: httpx.Response
    ) -> CheckResult:
        """Handle URL redirects."""
        redirects = 0
        current_url = original_url
        
        while redirects < self.max_redirects:
            if "location" not in response.headers:
                return CheckResult(
                    is_alive=False,
                    status_code=response.status_code,
                    error="Redirect without location header"
                )
            
            # Get redirect location
            location = response.headers["location"]
            if location.startswith("/"):
                # Relative to domain
                parsed = urlparse(current_url)
                location = f"{parsed.scheme}://{parsed.netloc}{location}"
            elif not location.startswith("http"):
                # Relative to path
                base = "/".join(current_url.split("/")[:-1])
                location = f"{base}/{location}"
            
            # Follow redirect
            try:
                response = await client.get(location)
                current_url = location
                redirects += 1
                
                if response.status_code < 300 or response.status_code >= 400:
                    break
                    
            except Exception as e:
                return CheckResult(
                    is_alive=False,
                    error=f"Redirect failed: {e}",
                    final_url=location
                )
        
        if redirects >= self.max_redirects:
            return CheckResult(
                is_alive=False,
                error=f"Too many redirects (>{self.max_redirects})"
            )
        
        # Check if redirected to different host
        original_host = urlparse(original_url).netloc
        final_host = urlparse(current_url).netloc
        
        return CheckResult(
            is_alive=response.status_code < 400,
            status_code=response.status_code,
            final_url=current_url,
            redirected=original_host != final_host
        )