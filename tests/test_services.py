"""
Test service layer functionality
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.scan_service import ScanService
from app.models import Scan, Website, Page, Issue
from app.schemas.scan import ScanCreate

class TestScanService:
    """Test scan service functionality"""
    
    @pytest.fixture
    def scan_service(self, test_session):
        return ScanService(test_session)
    
    async def test_create_scan(self, scan_service, sample_website):
        """Test creating a new scan"""
        scan_data = ScanCreate(
            website_id=sample_website.id,
            config={"max_depth": 3, "max_pages": 100}
        )
        
        scan = await scan_service.create_scan(scan_data)
        
        assert scan.website_id == sample_website.id
        assert scan.status == "pending"
        assert scan.config["max_depth"] == 3
        assert scan.id is not None
    
    async def test_get_scan_by_id(self, scan_service, sample_scan):
        """Test retrieving scan by ID"""
        scan = await scan_service.get_scan(sample_scan.id)
        
        assert scan is not None
        assert scan.id == sample_scan.id
        assert scan.website_id == sample_scan.website_id
    
    async def test_get_nonexistent_scan(self, scan_service):
        """Test retrieving non-existent scan"""
        scan = await scan_service.get_scan(99999)
        assert scan is None
    
    async def test_update_scan_status(self, scan_service, sample_scan):
        """Test updating scan status"""
        updated_scan = await scan_service.update_scan_status(
            sample_scan.id,
            "running",
            pages_found=50,
            pages_scanned=25
        )
        
        assert updated_scan.status == "running"
        assert updated_scan.pages_found == 50
        assert updated_scan.pages_scanned == 25
    
    async def test_complete_scan(self, scan_service, sample_scan):
        """Test completing a scan"""
        updated_scan = await scan_service.complete_scan(
            sample_scan.id,
            pages_scanned=100,
            pages_failed=5,
            total_issues=25
        )
        
        assert updated_scan.status == "completed"
        assert updated_scan.pages_scanned == 100
        assert updated_scan.pages_failed == 5
        assert updated_scan.total_issues == 25
        assert updated_scan.completed_at is not None
    
    async def test_fail_scan(self, scan_service, sample_scan):
        """Test marking scan as failed"""
        error_message = "Connection timeout"
        updated_scan = await scan_service.fail_scan(sample_scan.id, error_message)
        
        assert updated_scan.status == "failed"
        assert updated_scan.error_message == error_message
        assert updated_scan.completed_at is not None
    
    async def test_get_scans_by_website(self, scan_service, sample_website, sample_scan):
        """Test retrieving scans for a specific website"""
        scans = await scan_service.get_scans_by_website(sample_website.id)
        
        assert len(scans) >= 1
        assert all(scan.website_id == sample_website.id for scan in scans)
    
    async def test_get_recent_scans(self, scan_service, sample_scan):
        """Test retrieving recent scans"""
        scans = await scan_service.get_recent_scans(limit=10)
        
        assert len(scans) <= 10
        assert len(scans) >= 1
        # Should be ordered by creation date (newest first)
        if len(scans) > 1:
            for i in range(len(scans) - 1):
                assert scans[i].created_at >= scans[i + 1].created_at

class TestScanServiceIntegration:
    """Test scan service integration with analyzers"""
    
    @pytest.fixture
    def scan_service(self, test_session):
        return ScanService(test_session)
    
    @patch('app.services.scan_service.ScanService._analyze_page')
    async def test_process_scan_page(self, mock_analyze, scan_service, sample_scan):
        """Test processing a single page during scan"""
        # Mock the analysis result
        mock_analyze.return_value = {
            'analysis_data': {
                'title': 'Test Page',
                'meta_description': 'Test description',
                'word_count': 500,
                'status_code': 200
            },
            'issues': [
                {
                    'type': 'missing_h1',
                    'category': 'on_page',
                    'severity': 'high',
                    'title': 'Missing H1',
                    'description': 'Page missing H1 tag',
                    'recommendation': 'Add H1 tag',
                    'score_impact': -8.0
                }
            ],
            'score': 92.0
        }
        
        url = "https://example.com/test-page"
        result = await scan_service.process_scan_page(sample_scan.id, url)
        
        assert result is not None
        assert result['page'].url == url
        assert result['page'].scan_id == sample_scan.id
        assert len(result['issues']) == 1
        assert result['issues'][0].type == 'missing_h1'
        
        # Verify the mock was called
        mock_analyze.assert_called_once_with(url)
    
    @patch('app.services.scan_service.AsyncWebCrawler')
    async def test_crawl_website_discovery(self, mock_crawler_class, scan_service, sample_website):
        """Test website crawling for URL discovery"""
        # Mock crawler instance
        mock_crawler = AsyncMock()
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        
        # Mock crawl result
        mock_crawl_result = Mock()
        mock_crawl_result.links = {
            'internal': [
                'https://example.com/page1',
                'https://example.com/page2',
                'https://example.com/about'
            ],
            'external': ['https://external.com']
        }
        mock_crawler.arun.return_value = mock_crawl_result
        
        urls = await scan_service.discover_website_urls(
            sample_website.domain,
            max_pages=10,
            max_depth=2
        )
        
        assert len(urls) >= 3
        assert 'https://example.com/page1' in urls
        assert 'https://example.com/page2' in urls
        assert 'https://external.com' not in urls  # Should exclude external URLs
    
    async def test_calculate_scan_statistics(self, scan_service, sample_scan, test_session):
        """Test calculating scan statistics"""
        # Add some test pages and issues
        page1 = Page(
            scan_id=sample_scan.id,
            url="https://example.com/page1",
            title="Page 1",
            status_code=200,
            seo_score=85.0
        )
        page2 = Page(
            scan_id=sample_scan.id,
            url="https://example.com/page2",
            title="Page 2",
            status_code=404,
            seo_score=60.0
        )
        
        test_session.add_all([page1, page2])
        await test_session.commit()
        await test_session.refresh(page1)
        await test_session.refresh(page2)
        
        # Add issues
        issue1 = Issue(
            page_id=page1.id,
            type="missing_h1",
            category="on_page",
            severity="high",
            title="Missing H1",
            description="Test issue",
            recommendation="Add H1",
            score_impact=-8.0
        )
        issue2 = Issue(
            page_id=page2.id,
            type="http_error_404",
            category="technical",
            severity="critical",
            title="404 Error",
            description="Page not found",
            recommendation="Fix URL",
            score_impact=-15.0
        )
        
        test_session.add_all([issue1, issue2])
        await test_session.commit()
        
        # Calculate statistics
        stats = await scan_service.calculate_scan_statistics(sample_scan.id)
        
        assert stats['total_pages'] == 2
        assert stats['total_issues'] == 2
        assert stats['average_score'] == 72.5  # (85 + 60) / 2
        assert stats['critical_issues'] == 1
        assert stats['high_issues'] == 1
        assert stats['pages_with_errors'] == 1

class TestScanServiceErrorHandling:
    """Test scan service error handling"""
    
    @pytest.fixture
    def scan_service(self, test_session):
        return ScanService(test_session)
    
    async def test_update_nonexistent_scan(self, scan_service):
        """Test updating non-existent scan"""
        result = await scan_service.update_scan_status(99999, "running")
        assert result is None
    
    @patch('app.services.scan_service.ScanService._analyze_page')
    async def test_handle_page_analysis_error(self, mock_analyze, scan_service, sample_scan):
        """Test handling page analysis errors"""
        # Mock analysis to raise exception
        mock_analyze.side_effect = Exception("Network error")
        
        url = "https://example.com/error-page"
        result = await scan_service.process_scan_page(sample_scan.id, url)
        
        # Should handle error gracefully
        assert result is not None
        assert result['page'].url == url
        assert result['page'].status_code == 0  # Error status
        assert len(result['issues']) >= 1  # Should have error issue
        
        # Check for error issue
        error_issues = [issue for issue in result['issues'] if 'error' in issue.type.lower()]
        assert len(error_issues) >= 1
    
    async def test_scan_timeout_handling(self, scan_service, sample_scan):
        """Test scan timeout handling"""
        # This would be implemented when scan timeout logic is added
        pass

class TestScanServiceScheduling:
    """Test scan service scheduling functionality"""
    
    @pytest.fixture
    def scan_service(self, test_session):
        return ScanService(test_session)
    
    async def test_get_websites_due_for_scan(self, scan_service, sample_website):
        """Test identifying websites that need scanning"""
        # This would test the scheduling logic
        # For now, just test that the method exists and returns data
        websites = await scan_service.get_websites_due_for_scan()
        
        # Should return a list (may be empty in test environment)
        assert isinstance(websites, list)
    
    async def test_schedule_automatic_scan(self, scan_service, sample_website):
        """Test scheduling automatic scans"""
        # This would test the automatic scheduling functionality
        # Implementation depends on the scheduling system used (Celery, APScheduler, etc.)
        pass