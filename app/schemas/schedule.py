from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class ScheduleFrequency(str, Enum):
    hourly = "hourly"
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"

class ScheduleBase(BaseModel):
    website_id: int = Field(..., description="ID del sito web")
    frequency: ScheduleFrequency = Field(..., description="Frequenza di scansione")
    is_active: bool = Field(True, description="Se la programmazione è attiva")

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(BaseModel):
    frequency: Optional[ScheduleFrequency] = None
    is_active: Optional[bool] = None

class ScheduleResponse(ScheduleBase):
    id: int
    next_run_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    last_error: Optional[str] = None
    error_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True