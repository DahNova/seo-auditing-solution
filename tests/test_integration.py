"""
Integration tests for SEO Auditing Solution
"""
import pytest
from httpx import AsyncClient
from unittest.mock import Mock, patch
from fastapi import status

class TestFullScanWorkflow:
    """Test complete scan workflow from API to analysis"""
    
    async def test_complete_scan_workflow(self, test_client: AsyncClient, sample_client, sample_website):
        """Test complete scan workflow: create scan -> process -> results"""
        
        # 1. Create a new scan via API
        scan_data = {
            "website_id": sample_website.id,
            "config": {
                "max_depth": 2,
                "max_pages": 10,
                "timeout": 300
            }
        }
        
        response = await test_client.post("/api/v1/scans/", json=scan_data)
        assert response.status_code == status.HTTP_201_CREATED
        scan = response.json()
        scan_id = scan["id"]
        
        # 2. Verify scan was created with pending status
        response = await test_client.get(f"/api/v1/scans/{scan_id}")
        assert response.status_code == status.HTTP_200_OK
        scan_details = response.json()
        assert scan_details["status"] == "pending"
        assert scan_details["website_id"] == sample_website.id
        
        # 3. Simulate scan processing (would normally be done by Celery)
        # Update scan status to running
        update_data = {
            "status": "running",
            "pages_found": 5,
            "pages_scanned": 0
        }
        response = await test_client.put(f"/api/v1/scans/{scan_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        # 4. Complete the scan
        complete_data = {
            "status": "completed",
            "pages_scanned": 5,
            "pages_failed": 0,
            "total_issues": 12
        }
        response = await test_client.put(f"/api/v1/scans/{scan_id}", json=complete_data)
        assert response.status_code == status.HTTP_200_OK
        
        # 5. Verify final scan state
        response = await test_client.get(f"/api/v1/scans/{scan_id}")
        scan_final = response.json()
        assert scan_final["status"] == "completed"
        assert scan_final["pages_scanned"] == 5
        assert scan_final["total_issues"] == 12
    
    @patch('app.services.seo_analyzer.crawl4ai_analyzer.AsyncWebCrawler')
    async def test_scan_with_real_analysis(self, mock_crawler_class, test_client: AsyncClient, sample_website):
        """Test scan with mocked but realistic SEO analysis"""
        
        # Mock crawler to return realistic data
        mock_crawler = Mock()
        mock_crawler_class.return_value.__aenter__.return_value = mock_crawler
        
        # Mock crawl result with SEO issues
        mock_crawl_result = Mock()
        mock_crawl_result.url = "https://example.com"
        mock_crawl_result.status_code = 200
        mock_crawl_result.markdown = "# Short Title\n\nShort content."  # Thin content
        mock_crawl_result.cleaned_html = """
        <html>
            <head>
                <title>Short</title>  <!-- Too short -->
                <!-- Missing meta description -->
            </head>
            <body>
                <!-- Missing H1 -->
                <h2>Subheading</h2>
                <p>Short content.</p>
                <img src="image.jpg" alt="">  <!-- Missing alt text -->
            </body>
        </html>
        """
        mock_crawl_result.metadata = {
            'title': 'Short',
            'description': None
        }
        mock_crawl_result.media = {
            'images': [{'src': 'image.jpg', 'alt': ''}]
        }
        mock_crawl_result.links = {
            'internal': [],
            'external': []
        }
        
        mock_crawler.arun.return_value = mock_crawl_result
        
        # Create scan
        scan_data = {"website_id": sample_website.id}
        response = await test_client.post("/api/v1/scans/", json=scan_data)
        scan = response.json()
        scan_id = scan["id"]
        
        # Process the scan (this would trigger the analysis)
        # Note: In a real test, you'd call the actual service methods
        # For now, we'll simulate the result
        
        # The scan should detect multiple issues:
        # - Missing meta description
        # - Title too short  
        # - Missing H1
        # - Thin content
        # - Image missing alt text
        
        # Verify scan can be retrieved
        response = await test_client.get(f"/api/v1/scans/{scan_id}")
        assert response.status_code == status.HTTP_200_OK

class TestClientWebsiteScanRelationships:
    """Test relationships between clients, websites, and scans"""
    
    async def test_client_with_multiple_websites_and_scans(self, test_client: AsyncClient):
        """Test client with multiple websites, each with multiple scans"""
        
        # 1. Create client
        client_data = {
            "name": "Multi-Site Agency",
            "contact_email": "agency@multisite.com",
            "description": "Agency with multiple websites"
        }
        response = await test_client.post("/api/v1/clients/", json=client_data)
        client = response.json()
        client_id = client["id"]
        
        # 2. Create multiple websites for the client
        websites = []
        for i in range(3):
            website_data = {
                "client_id": client_id,
                "domain": f"https://site{i+1}.com",
                "name": f"Site {i+1}",
                "scan_frequency": "weekly"
            }
            response = await test_client.post("/api/v1/websites/", json=website_data)
            assert response.status_code == status.HTTP_201_CREATED
            websites.append(response.json())
        
        # 3. Create multiple scans for each website
        all_scans = []
        for website in websites:
            for j in range(2):  # 2 scans per website
                scan_data = {
                    "website_id": website["id"],
                    "config": {"max_pages": 100}
                }
                response = await test_client.post("/api/v1/scans/", json=scan_data)
                assert response.status_code == status.HTTP_201_CREATED
                all_scans.append(response.json())
        
        # 4. Verify relationships
        # Get all websites for the client
        response = await test_client.get("/api/v1/websites/")
        all_websites = response.json()
        client_websites = [w for w in all_websites if w["client_id"] == client_id]
        assert len(client_websites) == 3
        
        # Get all scans
        response = await test_client.get("/api/v1/scans/")
        all_scans_db = response.json()
        assert len(all_scans_db) >= 6  # At least our 6 scans
        
        # Verify each website has scans
        for website in client_websites:
            website_scans = [s for s in all_scans_db if s["website_id"] == website["id"]]
            assert len(website_scans) >= 2
    
    async def test_cascade_delete_behavior(self, test_client: AsyncClient):
        """Test cascade delete behavior when deleting clients/websites"""
        
        # 1. Create client, website, and scan
        client_data = {
            "name": "Delete Test Client",
            "contact_email": "delete@test.com"
        }
        response = await test_client.post("/api/v1/clients/", json=client_data)
        client = response.json()
        client_id = client["id"]
        
        website_data = {
            "client_id": client_id,
            "domain": "https://deletetest.com",
            "name": "Delete Test Site"
        }
        response = await test_client.post("/api/v1/websites/", json=website_data)
        website = response.json()
        website_id = website["id"]
        
        scan_data = {"website_id": website_id}
        response = await test_client.post("/api/v1/scans/", json=scan_data)
        scan = response.json()
        scan_id = scan["id"]
        
        # 2. Delete website (should also delete associated scans)
        response = await test_client.delete(f"/api/v1/websites/{website_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # 3. Verify website and scan are deleted
        response = await test_client.get(f"/api/v1/websites/{website_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response = await test_client.get(f"/api/v1/scans/{scan_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # 4. Client should still exist
        response = await test_client.get(f"/api/v1/clients/{client_id}")
        assert response.status_code == status.HTTP_200_OK

class TestAPIErrorHandling:
    """Test API error handling and edge cases"""
    
    async def test_concurrent_scan_requests(self, test_client: AsyncClient, sample_website):
        """Test handling of concurrent scan requests for same website"""
        
        # Create multiple scans for the same website simultaneously
        scan_data = {"website_id": sample_website.id}
        
        # In a real implementation, you might want to prevent multiple concurrent scans
        # For now, just verify all requests are handled properly
        responses = []
        for _ in range(3):
            response = await test_client.post("/api/v1/scans/", json=scan_data)
            responses.append(response)
        
        # All requests should succeed (or some should be rejected with appropriate status)
        for response in responses:
            assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_429_TOO_MANY_REQUESTS]
    
    async def test_invalid_scan_configuration(self, test_client: AsyncClient, sample_website):
        """Test handling of invalid scan configurations"""
        
        # Test with invalid max_pages (negative)
        scan_data = {
            "website_id": sample_website.id,
            "config": {
                "max_pages": -1,
                "max_depth": 5
            }
        }
        
        response = await test_client.post("/api/v1/scans/", json=scan_data)
        # Should either accept and sanitize, or reject with 422
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_422_UNPROCESSABLE_ENTITY]
        
        if response.status_code == status.HTTP_201_CREATED:
            # If accepted, should have sanitized the config
            scan = response.json()
            # Config should be corrected or use defaults
            assert scan["config"]["max_pages"] > 0
    
    async def test_scan_large_website_limits(self, test_client: AsyncClient, sample_website):
        """Test handling of scans with very large limits"""
        
        scan_data = {
            "website_id": sample_website.id,
            "config": {
                "max_pages": 100000,  # Very large number
                "max_depth": 50,      # Very deep
                "timeout": 86400      # 24 hours
            }
        }
        
        response = await test_client.post("/api/v1/scans/", json=scan_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        scan = response.json()
        # Should have reasonable limits applied
        assert scan["config"]["max_pages"] <= 10000  # Reasonable limit
        assert scan["config"]["max_depth"] <= 10     # Reasonable depth
        assert scan["config"]["timeout"] <= 3600     # Max 1 hour

class TestSystemIntegration:
    """Test integration with external systems and dependencies"""
    
    async def test_database_connection_handling(self, test_client: AsyncClient):
        """Test database connection handling under load"""
        
        # Make multiple concurrent requests to test connection pooling
        import asyncio
        
        async def make_request():
            return await test_client.get("/api/v1/clients/")
        
        # Create 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should succeed
        for response in responses:
            assert not isinstance(response, Exception)
            assert response.status_code == status.HTTP_200_OK
    
    async def test_health_check_under_load(self, test_client: AsyncClient):
        """Test health check endpoint under load"""
        
        # Health check should always respond quickly
        import time
        
        start_time = time.time()
        response = await test_client.get("/health")
        end_time = time.time()
        
        assert response.status_code == status.HTTP_200_OK
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    @patch('app.core.config.Settings')
    async def test_configuration_validation(self, mock_settings, test_client: AsyncClient):
        """Test that invalid configuration is handled gracefully"""
        
        # This would test configuration validation
        # In a real implementation, you'd test various config scenarios
        pass

class TestPerformanceBaseline:
    """Test performance baselines for the system"""
    
    async def test_api_response_times(self, test_client: AsyncClient, sample_client, sample_website):
        """Test that API responses are within acceptable time limits"""
        import time
        
        endpoints_to_test = [
            ("/api/v1/clients/", "GET"),
            ("/api/v1/websites/", "GET"),
            ("/api/v1/scans/", "GET"),
            (f"/api/v1/clients/{sample_client.id}", "GET"),
            (f"/api/v1/websites/{sample_website.id}", "GET")
        ]
        
        for endpoint, method in endpoints_to_test:
            start_time = time.time()
            
            if method == "GET":
                response = await test_client.get(endpoint)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            assert response.status_code == status.HTTP_200_OK
            assert response_time < 2.0  # Should respond within 2 seconds
    
    async def test_concurrent_user_simulation(self, test_client: AsyncClient):
        """Test system behavior with concurrent users"""
        import asyncio
        
        async def simulate_user_session():
            """Simulate a typical user session"""
            # List clients
            response = await test_client.get("/api/v1/clients/")
            assert response.status_code == status.HTTP_200_OK
            
            # List websites
            response = await test_client.get("/api/v1/websites/")
            assert response.status_code == status.HTTP_200_OK
            
            # List scans
            response = await test_client.get("/api/v1/scans/")
            assert response.status_code == status.HTTP_200_OK
            
            return True
        
        # Simulate 5 concurrent users
        tasks = [simulate_user_session() for _ in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All sessions should complete successfully
        for result in results:
            assert result is True or not isinstance(result, Exception)