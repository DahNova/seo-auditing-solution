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
        'missing_h1': -8.0,  # Increased - very important
        'multiple_h1': -4.0,  # Increased - confuses Google
        'empty_h1': -6.0,
        'h1_too_short': -3.0,
        'h1_too_long': -2.0,
        'duplicate_h1_title': -4.0,  # New - wastes SEO opportunity
        'h1_too_similar_title': -2.0,  # New - reduces keyword diversity
        'broken_heading_hierarchy': -3.0,
        'excessive_headings': -1.0,
        'images_missing_alt': -4.0,
        'images_bad_filename': -1.0,
        'oversized_images': -2.0,
        'thin_content': -5.0,
        'broken_links': -6.0
    }

# Global settings instances
settings = Settings()
seo_config = SEOConfig()