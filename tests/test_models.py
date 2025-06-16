"""
Test database models
"""
import pytest
from datetime import datetime
from sqlalchemy import select

from app.models import Client, Website, Scan, Page, Issue

class TestClientModel:
    """Test Client model"""
    
    async def test_create_client(self, test_session):
        """Test creating a client"""
        client = Client(
            name="Test Agency",
            contact_email="agency@test.com",
            description="Test description"
        )
        
        test_session.add(client)
        await test_session.commit()
        await test_session.refresh(client)
        
        assert client.id is not None
        assert client.name == "Test Agency"
        assert client.contact_email == "agency@test.com"
        assert client.created_at is not None
        
    async def test_client_relationships(self, test_session, sample_client):
        """Test client relationships with websites"""
        website = Website(
            client_id=sample_client.id,
            domain="https://test.com",
            name="Test Site"
        )
        
        test_session.add(website)
        await test_session.commit()
        
        # Test relationship
        result = await test_session.execute(
            select(Client).where(Client.id == sample_client.id)
        )
        client = result.scalar_one()
        
        assert len(client.websites) == 1
        assert client.websites[0].domain == "https://test.com"

class TestWebsiteModel:
    """Test Website model"""
    
    async def test_create_website(self, test_session, sample_client):
        """Test creating a website"""
        website = Website(
            client_id=sample_client.id,
            domain="https://example.com",
            name="Example Site",
            scan_frequency="weekly",
            max_pages=500,
            max_depth=3,
            robots_respect=True,
            include_external=False,
            is_active=True
        )
        
        test_session.add(website)
        await test_session.commit()
        await test_session.refresh(website)
        
        assert website.id is not None
        assert website.domain == "https://example.com"
        assert website.scan_frequency == "weekly"
        assert website.max_pages == 500
        assert website.is_active is True
        
    async def test_website_defaults(self, test_session, sample_client):
        """Test website default values"""
        website = Website(
            client_id=sample_client.id,
            domain="https://minimal.com"
        )
        
        test_session.add(website)
        await test_session.commit()
        await test_session.refresh(website)
        
        assert website.robots_respect is True
        assert website.scan_frequency == "monthly"
        assert website.max_pages == 1000
        assert website.max_depth == 5
        assert website.include_external is False
        assert website.is_active is True

class TestScanModel:
    """Test Scan model"""
    
    async def test_create_scan(self, test_session, sample_website):
        """Test creating a scan"""
        scan = Scan(
            website_id=sample_website.id,
            status="running",
            pages_found=100,
            pages_scanned=50,
            pages_failed=2,
            total_issues=15,
            config={"max_depth": 5, "timeout": 300}
        )
        
        test_session.add(scan)
        await test_session.commit()
        await test_session.refresh(scan)
        
        assert scan.id is not None
        assert scan.status == "running"
        assert scan.pages_found == 100
        assert scan.total_issues == 15
        assert scan.config["max_depth"] == 5
        
    async def test_scan_timestamps(self, test_session, sample_website):
        """Test scan timestamp handling"""
        scan = Scan(
            website_id=sample_website.id,
            status="completed"
        )
        
        test_session.add(scan)
        await test_session.commit()
        await test_session.refresh(scan)
        
        assert scan.created_at is not None
        assert scan.started_at is not None

class TestPageModel:
    """Test Page model"""
    
    async def test_create_page(self, test_session, sample_scan):
        """Test creating a page"""
        page = Page(
            scan_id=sample_scan.id,
            url="https://example.com/page1",
            title="Page 1 Title",
            meta_description="Page 1 description",
            status_code=200,
            word_count=750,
            load_time=1.2,
            h1_count=1,
            h2_count=3,
            image_count=5,
            link_count=10,
            internal_links=8,
            external_links=2
        )
        
        test_session.add(page)
        await test_session.commit()
        await test_session.refresh(page)
        
        assert page.id is not None
        assert page.url == "https://example.com/page1"
        assert page.status_code == 200
        assert page.word_count == 750
        
    async def test_page_relationships(self, test_session, sample_page):
        """Test page relationships with issues"""
        issue = Issue(
            page_id=sample_page.id,
            type="title_too_short",
            category="on_page",
            severity="medium",
            title="Title Too Short",
            description="Page title is too short",
            recommendation="Extend title length",
            score_impact=-3.0,
            status="open"
        )
        
        test_session.add(issue)
        await test_session.commit()
        
        # Test relationship
        result = await test_session.execute(
            select(Page).where(Page.id == sample_page.id)
        )
        page = result.scalar_one()
        
        assert len(page.issues) == 1
        assert page.issues[0].type == "title_too_short"

class TestIssueModel:
    """Test Issue model"""
    
    async def test_create_issue(self, test_session, sample_page):
        """Test creating an issue"""
        issue = Issue(
            page_id=sample_page.id,
            type="missing_h1",
            category="on_page",
            severity="high",
            title="Missing H1 Tag",
            description="Page is missing H1 tag",
            element="head",
            recommendation="Add H1 tag",
            score_impact=-8.0,
            status="open"
        )
        
        test_session.add(issue)
        await test_session.commit()
        await test_session.refresh(issue)
        
        assert issue.id is not None
        assert issue.type == "missing_h1"
        assert issue.severity == "high"
        assert issue.score_impact == -8.0
        assert issue.status == "open"
        assert issue.detected_at is not None
        
    async def test_issue_severity_values(self, test_session, sample_page):
        """Test different severity values"""
        severities = ["critical", "high", "medium", "low", "minor"]
        
        for severity in severities:
            issue = Issue(
                page_id=sample_page.id,
                type=f"test_{severity}",
                category="test",
                severity=severity,
                title=f"Test {severity} issue",
                description="Test description",
                recommendation="Test recommendation",
                score_impact=-1.0,
                status="open"
            )
            
            test_session.add(issue)
            await test_session.commit()
            await test_session.refresh(issue)
            
            assert issue.severity == severity