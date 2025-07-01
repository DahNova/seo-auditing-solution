from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, List, Any

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # Database
    database_url: str = "postgresql://seo_user:seo_password@postgres:5432/seo_auditing"
    database_echo: bool = False
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    
    # API
    secret_key: str = "your-secret-key-here"
    debug: bool = True
    workers: int = 4
    
    # Crawling
    max_concurrent_crawls: int = 5
    default_crawl_timeout: int = 300
    
    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("sqlite"):
            return self.database_url.replace("sqlite://", "sqlite+aiosqlite://")
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")

class SEOConfig(BaseSettings):
    """SEO analysis configuration"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    # Title optimization (2024/2025 standards)
    title_min_length: int = 50
    title_max_length: int = 60
    
    # Meta description optimization (mobile-first)
    meta_desc_min_length: int = 140
    meta_desc_max_length: int = 155
    
    # Content optimization (updated standards)
    min_word_count: int = 500  # 500+ words for quality content
    
    # H1 optimization  
    h1_min_length: int = 10
    h1_max_length: int = 70
    
    # Image optimization
    max_image_width: int = 1920
    max_image_height: int = 1080
    max_image_size_mb: float = 1.0
    
    # Bad filename patterns for images
    bad_filename_patterns: List[str] = [
        r'^img\d+\.(jpg|jpeg|png|gif|webp)$',
        r'^image\d+\.(jpg|jpeg|png|gif|webp)$',
        r'^dsc\d+\.(jpg|jpeg|png|gif|webp)$',
        r'^screenshot.*\.(jpg|jpeg|png|gif|webp)$',
        r'^untitled.*\.(jpg|jpeg|png|gif|webp)$'
    ]
    
    # Scoring weights (updated for modern SEO)
    scoring_weights: Dict[str, float] = {
        'missing_title': -10.0,
        'title_too_short': -4.0,  # Increased importance
        'title_too_long': -2.0,
        'missing_meta_description': -8.0,
        'meta_desc_too_short': -3.0,  # Increased importance
        'meta_desc_too_long': -2.0,
        'h1_mancante': -8.0,  # Increased - very important
        'h1_multipli': -4.0,  # Increased - confuses Google
        'empty_h1': -6.0,
        'h1_too_short': -3.0,
        'h1_too_long': -2.0,
        'duplicate_h1_title': -4.0,  # New - wastes SEO opportunity
        'h1_too_similar_title': -2.0,  # New - reduces keyword diversity
        'broken_heading_hierarchy': -3.0,
        'excessive_headings': -1.0,
        'image_missing_alt': -4.0,
        'image_bad_filename': -1.0,
        'image_oversized': -2.0,
        'contenuto_scarso': -5.0,
        'contenuto_insufficiente': -5.0,
        'broken_links': -6.0,
        # Content quality weights
        'poor_readability': -4.0,
        'keyword_stuffing': -6.0,
        'duplicate_content': -8.0,
        'canonical_mancante': -6.0,  # High impact for duplicate content prevention
        'outdated_content': -3.0,
        'missing_internal_links': -2.0,
        # Accessibility weights
        'poor_color_contrast': -3.0,
        'missing_accessibility_features': -4.0,
        'keyboard_navigation_issues': -3.0,
        # E-A-T weights
        'missing_author_info': -3.0,
        'poor_trust_signals': -4.0,
        'missing_contact_info': -2.0,
        # Local SEO weights
        'inconsistent_nap': -5.0,
        'missing_local_schema': -3.0
    }
    
    # Content quality thresholds
    readability_min_score: float = 8.0  # Flesch-Kincaid grade level
    readability_max_score: float = 12.0
    keyword_density_max: float = 3.0  # Maximum keyword density percentage
    
    # Accessibility standards
    min_color_contrast_ratio: float = 4.5  # WCAG AA standard
    
    # E-A-T signal indicators
    trust_signal_keywords: List[str] = [
        'about us', 'chi siamo', 'contatti', 'contact', 'privacy policy', 
        'termini di servizio', 'terms of service', 'certificazioni',
        'certifications', 'testimonials', 'recensioni'
    ]
    
    authority_signal_keywords: List[str] = [
        'esperto', 'expert', 'dottore', 'doctor', 'professore', 'professor',
        'certificato', 'certified', 'premio', 'award', 'pubblicazione', 'publication'
    ]
    
    # Local SEO patterns
    nap_patterns: Dict[str, str] = {
        'phone_it': r'(?:\+39|0039)?[\s\-]?(?:0\d{2,3}[\s\-]?\d{6,7}|\d{3}[\s\-]?\d{3}[\s\-]?\d{4})',
        'address_it': r'\b(?:via|viale|corso|piazza|largo|strada)\s+[A-Za-z\s,]+\d+\b'
    }

# Global settings instances
settings = Settings()
seo_config = SEOConfig()