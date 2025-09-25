"""Models for LinkAce Sentry."""

from typing import List, Optional
from pydantic import BaseModel


class Bookmark(BaseModel):
    """Bookmark model."""
    id: str
    url: str
    tags: List[str] = []
    title: Optional[str] = None
    note: Optional[str] = None


class Tag(BaseModel):
    """Tag model."""
    id: str
    name: str


class CheckResult(BaseModel):
    """URL check result."""
    is_alive: bool
    status_code: Optional[int] = None
    final_url: Optional[str] = None
    error: Optional[str] = None
    redirected: bool = False