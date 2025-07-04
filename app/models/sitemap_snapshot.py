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
    
    # Enterprise Sitemap Features
    sitemap_type = Column(String(20), default='regular')  # regular, index, image, video, news, mobile
    is_sitemap_index = Column(Boolean, default=False)  # True if this is a sitemap index
    parent_sitemap_url = Column(Text, nullable=True)  # Parent sitemap if this is a child
    child_sitemaps_count = Column(Integer, default=0)  # Number of child sitemaps if this is an index
    
    # Content analysis
    urls_list = Column(JSON, default=list)  # List of URLs found in sitemap
    urls_with_metadata = Column(JSON, default=list)  # Detailed URL data with priority, changefreq, lastmod
    priority_distribution = Column(JSON, default=dict)  # Distribution of priority values
    changefreq_distribution = Column(JSON, default=dict)  # Distribution of changefreq values
    image_urls_count = Column(Integer, default=0)  # Count of image URLs if image sitemap
    
    # Processing Statistics
    parsing_time = Column(Integer, nullable=True)  # Time taken to parse in seconds
    parsing_errors = Column(JSON, default=list)  # List of parsing errors encountered
    compressed_size = Column(Integer, nullable=True)  # Size if gzip compressed
    uncompressed_size = Column(Integer, nullable=True)  # Uncompressed size
    
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