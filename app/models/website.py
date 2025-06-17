from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Website(Base):
    __tablename__ = "websites"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    domain = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Scan configuration
    robots_respect = Column(Boolean, default=True)
    scan_frequency = Column(String(50), default="monthly")  # daily, weekly, monthly
    max_pages = Column(Integer, default=1000)
    max_depth = Column(Integer, default=5)
    include_external = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_scan_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    client = relationship("Client", back_populates="websites")
    scans = relationship("Scan", back_populates="website", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="website", cascade="all, delete-orphan")
    robots_snapshots = relationship("RobotsSnapshot", back_populates="website", cascade="all, delete-orphan")
    sitemap_snapshots = relationship("SitemapSnapshot", back_populates="website", cascade="all, delete-orphan")