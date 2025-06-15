from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class SitemapSnapshot(Base):
    __tablename__ = "sitemap_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    
    # Sitemap info
    sitemap_url = Column(Text, nullable=False)
    content_hash = Column(String(255), nullable=False, index=True)
    urls_count = Column(Integer, default=0)
    
    # Content analysis
    urls_list = Column(JSON, default=list)  # List of URLs found in sitemap
    last_modified = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_accessible = Column(Boolean, default=True)
    status_code = Column(Integer, nullable=True)
    
    # Change detection
    has_changed = Column(Boolean, default=False)
    previous_hash = Column(String(255), nullable=True)
    previous_urls_count = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    website = relationship("Website", back_populates="sitemap_snapshots")