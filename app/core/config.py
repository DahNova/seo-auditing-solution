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
    
    # Title optimization
    title_min_length: int = 30
    title_max_length: int = 60
    
    # Meta description optimization  
    meta_desc_min_length: int = 120
    meta_desc_max_length: int = 160
    
    # Content optimization
    min_word_count: int = 300
    
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
    
    # Scoring weights
    scoring_weights: Dict[str, float] = {
        'missing_title': -10.0,
        'title_too_short': -3.0,
        'title_too_long': -2.0,
        'missing_meta_description': -8.0,
        'meta_desc_too_short': -2.0,
        'meta_desc_too_long': -2.0,
        'missing_h1': -5.0,
        'multiple_h1': -3.0,
        'images_missing_alt': -4.0,
        'images_bad_filename': -1.0,
        'oversized_images': -2.0,
        'thin_content': -5.0,
        'broken_links': -6.0
    }

# Global settings instances
settings = Settings()
seo_config = SEOConfig()