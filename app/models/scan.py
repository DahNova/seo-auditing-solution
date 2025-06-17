from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    
    # Scan metadata
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Results summary
    pages_found = Column(Integer, default=0)
    pages_scanned = Column(Integer, default=0)
    pages_failed = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    seo_score = Column(Float, default=0.0)
    
    # Configuration used
    config = Column(JSON, nullable=True)
    
    # Errors/logs
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    website = relationship("Website", back_populates="scans")
    pages = relationship("Page", back_populates="scan", cascade="all, delete-orphan")