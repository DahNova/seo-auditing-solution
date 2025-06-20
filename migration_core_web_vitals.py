#!/usr/bin/env python3
"""
Database migration script to add Core Web Vitals and Technical SEO columns
This script safely adds new columns to the pages table
"""
import asyncio
import logging
from sqlalchemy import text
from app.database import engine as async_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQL commands to add new columns
MIGRATION_SQL = [
    # Core Web Vitals & Performance columns
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS performance_score DOUBLE PRECISION DEFAULT 0.0
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS lcp_score DOUBLE PRECISION
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS fid_score DOUBLE PRECISION
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS cls_score DOUBLE PRECISION
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS fcp_score DOUBLE PRECISION
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS ttfb_score DOUBLE PRECISION
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS core_web_vitals JSON DEFAULT '{}'
    """,
    
    # Technical SEO columns
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS technical_score DOUBLE PRECISION DEFAULT 0.0
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS has_schema_markup INTEGER DEFAULT 0
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS schema_types JSON DEFAULT '[]'
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS social_tags_score DOUBLE PRECISION DEFAULT 0.0
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS mobile_score DOUBLE PRECISION DEFAULT 0.0
    """,
    """
    ALTER TABLE pages 
    ADD COLUMN IF NOT EXISTS technical_seo_data JSON DEFAULT '{}'
    """
]

async def run_migration():
    """Run the database migration"""
    try:
        async with async_engine.begin() as conn:
            logger.info("Starting Core Web Vitals and Technical SEO migration...")
            
            for i, sql_command in enumerate(MIGRATION_SQL, 1):
                try:
                    logger.info(f"Executing migration step {i}/{len(MIGRATION_SQL)}")
                    await conn.execute(text(sql_command))
                    logger.info(f"✅ Migration step {i} completed successfully")
                except Exception as e:
                    logger.error(f"❌ Error in migration step {i}: {str(e)}")
                    # Continue with other commands - some might fail if columns already exist
                    continue
            
            logger.info("🎉 Migration completed successfully!")
            logger.info("New columns added to pages table:")
            logger.info("  - performance_score: Overall Core Web Vitals performance score")
            logger.info("  - lcp_score, fid_score, cls_score, fcp_score, ttfb_score: Individual CWV metrics")
            logger.info("  - core_web_vitals: Detailed CWV data (JSON)")
            logger.info("  - technical_score: Technical SEO score")
            logger.info("  - has_schema_markup: Whether page has schema markup")
            logger.info("  - schema_types: Types of schema found (JSON array)")
            logger.info("  - social_tags_score: Social media meta tags score")
            logger.info("  - mobile_score: Mobile optimization score")
            logger.info("  - technical_seo_data: Detailed technical SEO data (JSON)")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise

async def verify_migration():
    """Verify that the migration was successful"""
    try:
        async with async_engine.begin() as conn:
            logger.info("Verifying migration...")
            
            # Check if new columns exist
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'pages' 
                AND column_name IN (
                    'performance_score', 'lcp_score', 'fid_score', 'cls_score', 
                    'fcp_score', 'ttfb_score', 'core_web_vitals',
                    'technical_score', 'has_schema_markup', 'schema_types',
                    'social_tags_score', 'mobile_score', 'technical_seo_data'
                )
                ORDER BY column_name
            """))
            
            columns = [row[0] for row in result.fetchall()]
            expected_columns = [
                'cls_score', 'core_web_vitals', 'fcp_score', 'fid_score', 
                'has_schema_markup', 'lcp_score', 'mobile_score', 
                'performance_score', 'schema_types', 'social_tags_score', 
                'technical_score', 'technical_seo_data', 'ttfb_score'
            ]
            
            missing_columns = set(expected_columns) - set(columns)
            if missing_columns:
                logger.warning(f"⚠️  Missing columns: {missing_columns}")
            else:
                logger.info("✅ All new columns are present in the database")
                
            logger.info(f"Found {len(columns)} new columns: {columns}")
            
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {str(e)}")

if __name__ == "__main__":
    async def main():
        await run_migration()
        await verify_migration()
        
    asyncio.run(main())