#!/usr/bin/env python3
"""
Migration: Add canonical URL and URL quality fields to pages table
"""

import asyncio
import asyncpg
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from core.config import settings

async def run_migration():
    """Add new fields for canonical URL detection and URL quality analysis"""
    
    print("🔄 Connecting to database...")
    
    # Parse database URL
    import urllib.parse
    db_url = urllib.parse.urlparse(settings.database_url)
    
    conn = await asyncpg.connect(
        host=db_url.hostname,
        port=db_url.port,
        user=db_url.username,
        password=db_url.password,
        database=db_url.path.lstrip('/')
    )
    
    try:
        print("📊 Adding canonical URL and URL quality fields to pages table...")
        
        # Add new fields to pages table
        await conn.execute("""
            ALTER TABLE pages 
            ADD COLUMN IF NOT EXISTS canonical_url TEXT,
            ADD COLUMN IF NOT EXISTS is_canonical INTEGER DEFAULT 1,
            ADD COLUMN IF NOT EXISTS duplicate_group_id VARCHAR(255),
            ADD COLUMN IF NOT EXISTS url_quality_score FLOAT DEFAULT 100.0,
            ADD COLUMN IF NOT EXISTS url_structure_data JSONB DEFAULT '{}'::jsonb
        """)
        
        # Create indexes for performance
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_pages_canonical_url ON pages(canonical_url);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_pages_duplicate_group ON pages(duplicate_group_id);
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_pages_is_canonical ON pages(is_canonical);
        """)
        
        print("✅ Successfully added canonical URL and URL quality fields!")
        print("📈 Added indexes for optimal query performance")
        
        # Show migration status
        result = await conn.fetchrow("""
            SELECT COUNT(*) as total_pages,
                   COUNT(canonical_url) as pages_with_canonical,
                   AVG(url_quality_score) as avg_url_quality
            FROM pages
        """)
        
        if result['total_pages'] > 0:
            print(f"📊 Migration Stats:")
            print(f"   Total pages: {result['total_pages']}")
            print(f"   Pages with canonical: {result['pages_with_canonical']}")
            print(f"   Average URL quality score: {result['avg_url_quality']:.1f}")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    print("🚀 Starting canonical URL and URL quality migration...")
    asyncio.run(run_migration())
    print("🎉 Migration completed successfully!")