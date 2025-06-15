from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Issue(Base):
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    
    # Issue classification
    type = Column(String(100), nullable=False, index=True)  # meta_title, meta_desc, h_tags, images, etc.
    category = Column(String(50), nullable=False)  # technical, on_page, content
    severity = Column(String(20), nullable=False)  # critical, high, medium, low
    
    # Issue details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    element = Column(Text, nullable=True)  # Specific element that has the issue
    recommendation = Column(Text, nullable=True)
    
    # Scoring impact
    score_impact = Column(Float, default=0.0)  # How much this issue affects the score
    
    # Resolution tracking
    status = Column(String(20), default="open")  # open, resolved, ignored
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    page = relationship("Page", back_populates="issues")