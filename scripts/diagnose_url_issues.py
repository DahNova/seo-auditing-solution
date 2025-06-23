#!/usr/bin/env python3
"""
URL Diagnostic Script
Diagnose and fix URL issues in the database, particularly invisible characters
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import sessionmaker
from app.database import sync_engine
from app.models import Page
from app.services.url_utils import detect_invisible_characters, clean_url


def diagnose_database_urls():
    """Diagnose URL issues in the database"""
    
    # Create database session
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        print("🔍 Diagnosing URL Issues in Database")
        print("=" * 60)
        
        # Get all pages
        pages = session.query(Page).all()
        
        if not pages:
            print("ℹ️  No pages found in database")
            return
        
        print(f"📊 Analyzing {len(pages)} pages...")
        
        pages_with_issues = []
        total_invisible_chars = 0
        
        for page in pages:
            if not page.url:
                continue
                
            # Check for invisible characters
            detection = detect_invisible_characters(page.url)
            
            if detection['has_invisible']:
                pages_with_issues.append({
                    'page_id': page.id,
                    'scan_id': page.scan_id,
                    'original_url': page.url,
                    'clean_url': clean_url(page.url),
                    'invisible_chars': detection['characters'],
                    'positions': detection['positions']
                })
                total_invisible_chars += len(detection['characters'])
        
        print(f"\n📋 DIAGNOSIS RESULTS:")
        print(f"   Total pages analyzed: {len(pages)}")
        print(f"   Pages with URL issues: {len(pages_with_issues)}")
        print(f"   Total invisible characters found: {total_invisible_chars}")
        
        if pages_with_issues:
            print(f"\n🚨 PROBLEMATIC URLS FOUND:")
            print("-" * 80)
            
            for issue in pages_with_issues:
                print(f"\nPage ID: {issue['page_id']} (Scan: {issue['scan_id']})")
                print(f"Original URL: {repr(issue['original_url'])}")
                print(f"Clean URL:    {repr(issue['clean_url'])}")
                print(f"Invisible characters found:")
                for char_info in issue['invisible_chars']:
                    print(f"  - {char_info['unicode_name']} ({char_info['unicode_code']}) at position {char_info['position']}")
        else:
            print("✅ No URL issues found! All URLs are clean.")
        
        return pages_with_issues
        
    finally:
        session.close()


def fix_database_urls(dry_run=True):
    """Fix URL issues in the database"""
    
    # Create database session
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    
    try:
        print(f"\n🔧 {'DRY RUN - ' if dry_run else ''}Fixing URL Issues in Database")
        print("=" * 60)
        
        pages_with_issues = []
        
        # Get all pages
        pages = session.query(Page).all()
        
        for page in pages:
            if not page.url:
                continue
                
            # Check if URL needs cleaning
            clean_url_value = clean_url(page.url)
            
            if page.url != clean_url_value:
                pages_with_issues.append({
                    'page': page,
                    'original_url': page.url,
                    'clean_url': clean_url_value
                })
        
        if not pages_with_issues:
            print("✅ No URLs need fixing!")
            return
        
        print(f"🔧 Found {len(pages_with_issues)} URLs that need fixing:")
        
        for issue in pages_with_issues:
            page = issue['page']
            print(f"\nPage ID {page.id}:")
            print(f"  Before: {repr(issue['original_url'])}")
            print(f"  After:  {repr(issue['clean_url'])}")
            
            if not dry_run:
                page.url = issue['clean_url']
                # Also clean canonical_url if it exists
                if page.canonical_url:
                    page.canonical_url = clean_url(page.canonical_url)
        
        if not dry_run:
            session.commit()
            print(f"\n✅ Successfully fixed {len(pages_with_issues)} URLs!")
        else:
            print(f"\n🔍 DRY RUN COMPLETE - {len(pages_with_issues)} URLs would be fixed")
            print("    Run with --fix to actually apply changes")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error fixing URLs: {e}")
        raise
    finally:
        session.close()


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnose and fix URL issues in the database')
    parser.add_argument('--fix', action='store_true', help='Actually fix the URLs (default is dry run)')
    parser.add_argument('--diagnose-only', action='store_true', help='Only diagnose, do not attempt to fix')
    
    args = parser.parse_args()
    
    # Always run diagnosis first
    issues = diagnose_database_urls()
    
    if not args.diagnose_only and issues:
        # If there are issues and we're not in diagnose-only mode, offer to fix
        if args.fix:
            fix_database_urls(dry_run=False)
        else:
            fix_database_urls(dry_run=True)
    
    print("\n🏁 URL diagnosis complete!")


if __name__ == "__main__":
    main()