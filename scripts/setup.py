#!/usr/bin/env python3
"""
Setup script for SEO Auditing Solution
"""
import asyncio
import sys
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Add project root to path
sys.path.append('.')

from app.core.config import settings
from app.database import init_db
from app.models import Client, Website

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_sample_data():
    """Create sample clients and websites for testing"""
    from app.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        # Check if data already exists
        from sqlalchemy import select
        result = await db.execute(select(Client))
        if result.first():
            logger.info("Sample data already exists")
            return
        
        # Create sample client
        client = Client(
            name="Dexa Agency",
            description="Sample client for testing",
            contact_email="test@dexa.com"
        )
        db.add(client)
        await db.flush()
        
        # Create sample websites
        websites_data = [
            {
                "client_id": client.id,
                "domain": "example.com",
                "name": "Example Website",
                "scan_frequency": "weekly",
                "max_pages": 100,
                "max_depth": 3
            },
            {
                "client_id": client.id,
                "domain": "test-site.com", 
                "name": "Test Site",
                "scan_frequency": "monthly",
                "max_pages": 200,
                "max_depth": 5
            }
        ]
        
        for website_data in websites_data:
            website = Website(**website_data)
            db.add(website)
        
        await db.commit()
        logger.info(f"Created sample client '{client.name}' with {len(websites_data)} websites")

async def test_database_connection():
    """Test database connection"""
    try:
        engine = create_async_engine(settings.async_database_url)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
            logger.info("✅ Database connection successful")
        await engine.dispose()
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

async def test_redis_connection():
    """Test Redis connection"""
    try:
        import redis.asyncio as redis
        r = redis.from_url(settings.redis_url)
        await r.ping()
        logger.info("✅ Redis connection successful")
        await r.close()
        return True
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        return False

async def main():
    """Main setup function"""
    logger.info("🚀 Setting up SEO Auditing Solution...")
    
    # Test connections
    db_ok = await test_database_connection()
    redis_ok = await test_redis_connection()
    
    if not db_ok:
        logger.error("Database connection failed. Make sure PostgreSQL is running.")
        return False
    
    if not redis_ok:
        logger.error("Redis connection failed. Make sure Redis is running.")
        return False
    
    # Initialize database
    logger.info("📊 Initializing database tables...")
    await init_db()
    
    # Create sample data
    logger.info("📝 Creating sample data...")
    await create_sample_data()
    
    logger.info("✅ Setup completed successfully!")
    logger.info("\n🌐 You can now:")
    logger.info("  - Access API docs: http://localhost:8000/docs")
    logger.info("  - Access Adminer: http://localhost:8080")
    logger.info("  - Test endpoints with sample data")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)