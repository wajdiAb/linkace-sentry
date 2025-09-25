from fastapi import APIRouter, HTTPException
from services.bookmark_checker import check_bookmarks
from services.linkace_client import list_bookmarks

router = APIRouter()

@router.get("/healthz")
async def health_check():
    return {"status": "healthy"}

@router.get("/metrics")
async def metrics():
    # Placeholder for metrics endpoint
    return {"metrics": "not implemented"}

@router.post("/run-once")
async def run_once():
    try:
        bookmarks = await list_bookmarks()
        dead_links = await check_bookmarks(bookmarks)
        return {"dead_links": dead_links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))