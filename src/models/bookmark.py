from pydantic import BaseModel
from typing import List, Optional

class Tag(BaseModel):
    name: str
    color: Optional[str] = None

class Bookmark(BaseModel):
    id: int
    title: str
    url: str
    tags: List[Tag] = []