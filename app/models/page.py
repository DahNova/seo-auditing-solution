from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Page(Base):
    __tablename__ = "pages"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    
    # Page info
    url = Column(Text, nullable=False, index=True)
    status_code = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)
    
    # SEO elements
    title = Column(Text, nullable=True)
    meta_description = Column(Text, nullable=True)
    h1_tags = Column(JSON, default=list)  # List of H1 texts
    h2_tags = Column(JSON, default=list)  # List of H2 texts
    h3_tags = Column(JSON, default=list)  # List of H3 texts
    
    # Images analysis
    total_images = Column(Integer, default=0)
    images_without_alt = Column(Integer, default=0)
    oversized_images = Column(Integer, default=0)
    images_bad_filename = Column(Integer, default=0)
    
    # Links analysis
    internal_links = Column(Integer, default=0)
    external_links = Column(Integer, default=0)
    broken_links = Column(Integer, default=0)
    
    # Content analysis
    word_count = Column(Integer, default=0)
    content_hash = Column(String(255), nullable=True)
    
    # Scoring
    seo_score = Column(Float, default=0.0)
    issues_count = Column(Integer, default=0)
    
    # Core Web Vitals & Performance
    performance_score = Column(Float, default=0.0)
    lcp_score = Column(Float, nullable=True)  # Largest Contentful Paint
    fid_score = Column(Float, nullable=True)  # First Input Delay
    cls_score = Column(Float, nullable=True)  # Cumulative Layout Shift
    fcp_score = Column(Float, nullable=True)  # First Contentful Paint
    ttfb_score = Column(Float, nullable=True)  # Time to First Byte
    core_web_vitals = Column(JSON, default=dict)  # Detailed CWV data
    
    # Technical SEO
    technical_score = Column(Float, default=0.0)
    has_schema_markup = Column(Integer, default=0)  # Boolean as int
    schema_types = Column(JSON, default=list)  # List of schema types found
    social_tags_score = Column(Float, default=0.0)
    mobile_score = Column(Float, default=0.0)
    technical_seo_data = Column(JSON, default=dict)  # Detailed technical data
    
    # Canonical and Deduplication
    canonical_url = Column(Text, nullable=True, index=True)  # Canonical URL from link tag
    is_canonical = Column(Integer, default=1)  # Boolean: is this the canonical version?
    duplicate_group_id = Column(String(255), nullable=True, index=True)  # Group ID for duplicates
    
    # URL Quality
    url_quality_score = Column(Float, default=100.0)  # URL structure quality score
    url_structure_data = Column(JSON, default=dict)  # Detailed URL analysis
    
    # URL Discovery Metadata (Enterprise Features)
    discovery_source = Column(String(50), nullable=True, index=True)  # sitemap, crawl, manual, robots, feed
    discovery_priority = Column(Float, nullable=True)  # Original discovery priority
    sitemap_priority = Column(Float, nullable=True)  # Original sitemap priority (0.0-1.0)
    sitemap_changefreq = Column(String(20), nullable=True)  # always, hourly, daily, weekly, monthly, yearly, never
    sitemap_lastmod = Column(DateTime(timezone=True), nullable=True)  # Last modified from sitemap
    source_sitemap_url = Column(Text, nullable=True)  # Which sitemap contained this URL
    parent_url = Column(Text, nullable=True)  # Parent URL if discovered via crawling
    crawl_depth = Column(Integer, default=0)  # Depth from homepage (0 = homepage)
    
    # Processing Metadata
    queue_priority = Column(String(20), nullable=True)  # critical, high, medium, low, deferred
    processing_started = Column(DateTime(timezone=True), nullable=True)
    processing_completed = Column(DateTime(timezone=True), nullable=True)
    estimated_processing_time = Column(Integer, nullable=True)  # Estimated time in seconds
    actual_processing_time = Column(Integer, nullable=True)  # Actual time in seconds
    
    # Retry and Error Handling
    retry_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed, skipped, retry
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scan = relationship("Scan", back_populates="pages")
    issues = relationship("Issue", back_populates="page", cascade="all, delete-orphan")