from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class ScanBase(BaseModel):
    status: str = Field("pending", pattern="^(pending|running|completed|failed)$")

class ScanCreate(BaseModel):
    website_id: int

class ScanUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|running|completed|failed)$")
    completed_at: Optional[datetime] = None
    pages_found: Optional[int] = Field(None, ge=0)
    pages_scanned: Optional[int] = Field(None, ge=0)
    pages_failed: Optional[int] = Field(None, ge=0)
    total_issues: Optional[int] = Field(None, ge=0)
    error_message: Optional[str] = None

class ScanResponse(ScanBase):
    id: int
    website_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    pages_found: int = 0
    pages_scanned: int = 0
    pages_failed: int = 0
    total_issues: int = 0
    config: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True