from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class IssueResponse(BaseModel):
    id: int
    page_id: int
    type: str = Field(..., max_length=100)
    category: str = Field(..., max_length=50)
    severity: str = Field(..., pattern="^(critical|high|medium|low)$")
    title: str = Field(..., max_length=255)
    description: str
    element: Optional[str] = None
    recommendation: Optional[str] = None
    score_impact: float = 0.0
    status: str = Field("open", pattern="^(open|resolved|ignored)$")
    resolved_at: Optional[datetime] = None
    detected_at: datetime
    
    class Config:
        from_attributes = True