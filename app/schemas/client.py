from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    contact_email: Optional[str] = Field(None, max_length=255)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    contact_email: Optional[str] = Field(None, max_length=255)

class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True