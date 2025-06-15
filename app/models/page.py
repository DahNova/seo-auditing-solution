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
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    scan = relationship("Scan", back_populates="pages")
    issues = relationship("Issue", back_populates="page", cascade="all, delete-orphan")