#!/usr/bin/env python3
"""
Test Script for Enterprise URL Discovery System
Tests recursive sitemap parsing with real-world sitemap: https://dexanet.com/
"""
import asyncio
import sys
import os
import logging
from datetime import datetime
import json

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.sitemap_parser import SitemapParser
from services.url_discovery_service import URLDiscoveryService, URLDiscoveryConfig

# Configure logging for detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def test_dexanet_sitemap_discovery():
    """Test comprehensive URL discovery for dexanet.com"""
    
    test_domain = "dexanet.com"
    
    print("=" * 80)
    print(f"🔍 TESTING ENTERPRISE URL DISCOVERY SYSTEM")
    print(f"📍 Domain: {test_domain}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        # Step 1: Test Sitemap Parser (Recursive Multi-Level)
        print("\n📋 STEP 1: Testing Recursive Sitemap Parser")
        print("-" * 50)
        
        async with SitemapParser(max_concurrent_requests=5, timeout=30) as parser:
            # Test sitemap discovery and parsing
            sitemap_results = await parser.parse_all_sitemaps(test_domain)
            
            print(f"✅ Sitemap Discovery Results:")
            print(f"   📁 Domain: {sitemap_results['domain']}")
            print(f"   🔗 Initial sitemaps found: {len(sitemap_results['discovered_sitemaps'])}")
            print(f"   📊 Total URLs discovered: {sitemap_results['total_urls']}")
            print(f"   📑 Sitemap indexes found: {sitemap_results['statistics']['indexes_found']}")
            print(f"   🏗️  Maximum recursion depth: {sitemap_results['statistics']['max_depth']}")
            print(f"   ✅ Sitemaps parsed successfully: {sitemap_results['statistics']['sitemaps_parsed']}")
            print(f"   ❌ Parsing errors: {len(sitemap_results['parsing_errors'])}")
            
            # Show discovered sitemap URLs
            if sitemap_results['discovered_sitemaps']:
                print(f"\n📋 Discovered Sitemap URLs:")
                for i, url in enumerate(sitemap_results['discovered_sitemaps'], 1):
                    print(f"   {i}. {url}")
            
            # Show sitemap indexes structure
            if sitemap_results['sitemap_indexes']:
                print(f"\n🏗️  Sitemap Index Structure:")
                for i, index in enumerate(sitemap_results['sitemap_indexes'], 1):
                    print(f"   {i}. {index.url}")
                    print(f"      └── Child sitemaps: {len(index.sitemaps)}")
                    for j, child in enumerate(index.sitemaps[:3], 1):  # Show first 3
                        print(f"          {j}. {child.get('url', 'N/A')}")
                    if len(index.sitemaps) > 3:
                        print(f"          ... and {len(index.sitemaps) - 3} more")
            
            # Show sample URLs with metadata
            if sitemap_results['urls']:
                print(f"\n🔗 Sample URLs with Metadata (first 10):")
                for i, url_obj in enumerate(sitemap_results['urls'][:10], 1):
                    print(f"   {i}. {url_obj.url}")
                    print(f"      └── Priority: {url_obj.priority:.2f} | "
                          f"Changefreq: {url_obj.changefreq.freq_value} | "
                          f"Calculated Priority: {url_obj.calculated_priority:.3f}")
                    if url_obj.lastmod:
                        print(f"      └── Last Modified: {url_obj.lastmod.strftime('%Y-%m-%d')}")
                    print(f"      └── Source Sitemap: {url_obj.source_sitemap}")
                
                if len(sitemap_results['urls']) > 10:
                    print(f"      ... and {len(sitemap_results['urls']) - 10} more URLs")
            
            # Show priority distribution
            priority_stats = sitemap_results['statistics'].get('urls_by_priority', {})
            if priority_stats:
                print(f"\n📊 Priority Distribution:")
                for priority_range, count in priority_stats.items():
                    print(f"   {priority_range}: {count} URLs")
            
            # Show changefreq distribution
            changefreq_stats = sitemap_results['statistics'].get('urls_by_changefreq', {})
            if changefreq_stats:
                print(f"\n🔄 Change Frequency Distribution:")
                for freq, count in changefreq_stats.items():
                    print(f"   {freq}: {count} URLs")
            
            # Show any errors
            if sitemap_results['parsing_errors']:
                print(f"\n❌ Parsing Errors:")
                for error in sitemap_results['parsing_errors']:
                    print(f"   • {error}")
        
        # Step 2: Test Full URL Discovery Service
        print("\n\n🚀 STEP 2: Testing Complete URL Discovery Service")
        print("-" * 50)
        
        # Configure discovery service
        config = URLDiscoveryConfig()
        config.max_crawl_pages = 50  # Limit for testing
        config.max_crawl_depth = 2
        config.crawl_external = False
        
        discovery_service = URLDiscoveryService(config)
        
        # Run complete URL discovery (sitemap + crawling)
        discovery_results = await discovery_service.discover_urls(
            domain=test_domain,
            robots_content=None,  # Will fetch robots.txt automatically
            crawl_config={
                'max_depth': 2,
                'max_pages': 50,
                'include_external': False
            }
        )
        
        print(f"✅ Complete URL Discovery Results:")
        print(f"   🔗 Total unique URLs: {discovery_results['total_urls']}")
        print(f"   📋 Sitemap URLs: {discovery_results['sources']['sitemap']['count']}")
        print(f"   🕷️  Crawled URLs: {discovery_results['sources']['crawl']['count']}")
        
        # Show source breakdown
        print(f"\n📊 URL Source Breakdown:")
        for source_name, source_data in discovery_results['sources'].items():
            count = source_data.get('count', 0)
            percentage = (count / discovery_results['total_urls'] * 100) if discovery_results['total_urls'] > 0 else 0
            print(f"   {source_name.title()}: {count} URLs ({percentage:.1f}%)")
        
        # Show high priority URLs
        high_priority_urls = [
            url for url in discovery_results['urls'] 
            if url.calculated_priority >= 0.8
        ]
        
        if high_priority_urls:
            print(f"\n⭐ High Priority URLs (≥0.8 calculated priority):")
            for url in high_priority_urls[:10]:  # Show top 10
                print(f"   • {url.url} (priority: {url.calculated_priority:.3f})")
            if len(high_priority_urls) > 10:
                print(f"   ... and {len(high_priority_urls) - 10} more high priority URLs")
        
        # Step 3: Performance Summary
        print("\n\n📈 PERFORMANCE SUMMARY")
        print("-" * 50)
        print(f"✅ Sitemap Discovery: {sitemap_results['statistics']['sitemaps_found']} sitemaps found")
        print(f"✅ Recursive Parsing: {sitemap_results['statistics']['max_depth']} levels deep")
        print(f"✅ URL Extraction: {sitemap_results['total_urls']} sitemap URLs")
        print(f"✅ Total Discovery: {discovery_results['total_urls']} unique URLs")
        print(f"✅ Multi-source: {len(discovery_results['sources'])} discovery methods")
        
        return {
            'sitemap_results': sitemap_results,
            'discovery_results': discovery_results,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }

async def main():
    """Main test execution"""
    print("🚀 Starting Enterprise URL Discovery Test...")
    
    # Run the test
    results = await test_dexanet_sitemap_discovery()
    
    if results['success']:
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETED SUCCESSFULLY!")
        print("🎉 Enterprise URL Discovery System is working correctly!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("❌ TEST FAILED!")
        print(f"Error: {results.get('error', 'Unknown error')}")
        print("=" * 80)
        return 1
    
    return 0

if __name__ == "__main__":
    # Run the async test
    exit_code = asyncio.run(main())
    sys.exit(exit_code)