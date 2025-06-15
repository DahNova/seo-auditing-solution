from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PageResponse(BaseModel):
    id: int
    scan_id: int
    url: str
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    h1_tags: List[str] = []
    h2_tags: List[str] = []
    h3_tags: List[str] = []
    total_images: int = 0
    images_without_alt: int = 0
    oversized_images: int = 0
    images_bad_filename: int = 0
    internal_links: int = 0
    external_links: int = 0
    broken_links: int = 0
    word_count: int = 0
    content_hash: Optional[str] = None
    seo_score: float = 0.0
    issues_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True