from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional

class WebsiteBase(BaseModel):
    domain: str = Field(..., min_length=1, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    robots_respect: bool = True
    scan_frequency: str = Field("monthly", pattern="^(daily|weekly|monthly)$")
    max_pages: int = Field(1000, ge=1, le=10000)
    max_depth: int = Field(5, ge=1, le=20)
    include_external: bool = False
    is_active: bool = True

class WebsiteCreate(WebsiteBase):
    client_id: int

class WebsiteUpdate(BaseModel):
    domain: Optional[str] = Field(None, min_length=1, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    robots_respect: Optional[bool] = None
    scan_frequency: Optional[str] = Field(None, pattern="^(daily|weekly|monthly)$")
    max_pages: Optional[int] = Field(None, ge=1, le=10000)
    max_depth: Optional[int] = Field(None, ge=1, le=20)
    include_external: Optional[bool] = None
    is_active: Optional[bool] = None

class WebsiteResponse(WebsiteBase):
    id: int
    client_id: int
    last_scan_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True