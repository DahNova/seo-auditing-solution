from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class RobotsSnapshot(Base):
    __tablename__ = "robots_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    
    # Content tracking
    content_hash = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=True)
    content_size = Column(Integer, default=0)
    
    # Status
    is_accessible = Column(Boolean, default=True)
    status_code = Column(Integer, nullable=True)
    
    # Change detection
    has_changed = Column(Boolean, default=False)
    previous_hash = Column(String(255), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    website = relationship("Website", back_populates="robots_snapshots")