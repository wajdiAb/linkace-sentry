from httpx import AsyncClient, Response
from fastapi import HTTPException
from typing import List, Dict

async def check_url(url: str) -> Dict[str, str]:
    try:
        async with AsyncClient() as client:
            response: Response = await client.head(url, allow_redirects=True)
            if response.status_code == 200:
                return {"url": url, "status": "alive"}
            else:
                return {"url": url, "status": "dead", "status_code": response.status_code}
    except Exception as e:
        return {"url": url, "status": "error", "error": str(e)}

async def check_bookmarks(bookmarks: List[str]) -> List[Dict[str, str]]:
    results = []
    for bookmark in bookmarks:
        result = await check_url(bookmark)
        results.append(result)
    return results