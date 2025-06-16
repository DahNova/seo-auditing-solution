from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class PageInfo(BaseModel):
    id: int
    url: str
    title: Optional[str] = None
    
    class Config:
        from_attributes = True

class IssueResponse(BaseModel):
    id: int
    page_id: int
    type: str = Field(..., max_length=100)
    category: str = Field(..., max_length=50)
    severity: str = Field(..., pattern="^(critical|high|medium|low|minor)$")
    title: str = Field(..., max_length=255)
    description: str
    element: Optional[str] = None
    recommendation: Optional[str] = None
    score_impact: float = 0.0
    status: str = Field("open", pattern="^(open|resolved|ignored)$")
    resolved_at: Optional[datetime] = None
    detected_at: datetime
    page: Optional[PageInfo] = None
    
    class Config:
        from_attributes = True