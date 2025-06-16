"""
Test API endpoints
"""
import pytest
from httpx import AsyncClient
from fastapi import status

class TestClientsAPI:
    """Test client management API endpoints"""
    
    async def test_create_client(self, test_client: AsyncClient):
        """Test creating a new client"""
        client_data = {
            "name": "Test Agency",
            "contact_email": "test@agency.com",
            "description": "Test agency description"
        }
        
        response = await test_client.post("/api/v1/clients/", json=client_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == client_data["name"]
        assert data["contact_email"] == client_data["contact_email"]
        assert "id" in data
        assert "created_at" in data
    
    async def test_get_clients(self, test_client: AsyncClient, sample_client):
        """Test retrieving clients list"""
        response = await test_client.get("/api/v1/clients/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert any(client["id"] == sample_client.id for client in data)
    
    async def test_get_client_by_id(self, test_client: AsyncClient, sample_client):
        """Test retrieving specific client"""
        response = await test_client.get(f"/api/v1/clients/{sample_client.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_client.id
        assert data["name"] == sample_client.name
    
    async def test_update_client(self, test_client: AsyncClient, sample_client):
        """Test updating client information"""
        update_data = {
            "name": "Updated Agency Name",
            "contact_email": "updated@agency.com",
            "description": "Updated description"
        }
        
        response = await test_client.put(f"/api/v1/clients/{sample_client.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["contact_email"] == update_data["contact_email"]
    
    async def test_delete_client(self, test_client: AsyncClient, sample_client):
        """Test deleting a client"""
        response = await test_client.delete(f"/api/v1/clients/{sample_client.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify client is deleted
        get_response = await test_client.get(f"/api/v1/clients/{sample_client.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    async def test_get_nonexistent_client(self, test_client: AsyncClient):
        """Test retrieving non-existent client"""
        response = await test_client.get("/api/v1/clients/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestWebsitesAPI:
    """Test website management API endpoints"""
    
    async def test_create_website(self, test_client: AsyncClient, sample_client):
        """Test creating a new website"""
        website_data = {
            "client_id": sample_client.id,
            "domain": "https://testsite.com",
            "name": "Test Website",
            "description": "Test website description",
            "scan_frequency": "weekly",
            "max_pages": 500,
            "max_depth": 3
        }
        
        response = await test_client.post("/api/v1/websites/", json=website_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["domain"] == website_data["domain"]
        assert data["client_id"] == sample_client.id
        assert "id" in data
    
    async def test_get_websites(self, test_client: AsyncClient, sample_website):
        """Test retrieving websites list"""
        response = await test_client.get("/api/v1/websites/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_get_website_by_id(self, test_client: AsyncClient, sample_website):
        """Test retrieving specific website"""
        response = await test_client.get(f"/api/v1/websites/{sample_website.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_website.id
        assert data["domain"] == sample_website.domain
    
    async def test_update_website(self, test_client: AsyncClient, sample_website):
        """Test updating website information"""
        update_data = {
            "name": "Updated Website Name",
            "description": "Updated description",
            "scan_frequency": "daily",
            "max_pages": 1500
        }
        
        response = await test_client.put(f"/api/v1/websites/{sample_website.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["scan_frequency"] == update_data["scan_frequency"]
    
    async def test_delete_website(self, test_client: AsyncClient, sample_website):
        """Test deleting a website"""
        response = await test_client.delete(f"/api/v1/websites/{sample_website.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify website is deleted
        get_response = await test_client.get(f"/api/v1/websites/{sample_website.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

class TestScansAPI:
    """Test scan management API endpoints"""
    
    async def test_create_scan(self, test_client: AsyncClient, sample_website):
        """Test creating a new scan"""
        scan_data = {
            "website_id": sample_website.id,
            "config": {
                "max_depth": 3,
                "max_pages": 500,
                "timeout": 300
            }
        }
        
        response = await test_client.post("/api/v1/scans/", json=scan_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["website_id"] == sample_website.id
        assert data["status"] == "pending"
        assert "id" in data
    
    async def test_get_scans(self, test_client: AsyncClient, sample_scan):
        """Test retrieving scans list"""
        response = await test_client.get("/api/v1/scans/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_get_scan_by_id(self, test_client: AsyncClient, sample_scan):
        """Test retrieving specific scan"""
        response = await test_client.get(f"/api/v1/scans/{sample_scan.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == sample_scan.id
        assert data["website_id"] == sample_scan.website_id
    
    async def test_update_scan_status(self, test_client: AsyncClient, sample_scan):
        """Test updating scan status"""
        update_data = {
            "status": "running",
            "pages_found": 25,
            "pages_scanned": 10
        }
        
        response = await test_client.put(f"/api/v1/scans/{sample_scan.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == update_data["status"]
        assert data["pages_found"] == update_data["pages_found"]

class TestHealthCheck:
    """Test health check and system endpoints"""
    
    async def test_health_check(self, test_client: AsyncClient):
        """Test health check endpoint"""
        response = await test_client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    async def test_api_docs_accessible(self, test_client: AsyncClient):
        """Test that API documentation is accessible"""
        response = await test_client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
    
    async def test_openapi_schema(self, test_client: AsyncClient):
        """Test OpenAPI schema endpoint"""
        response = await test_client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "openapi" in data
        assert "paths" in data

class TestValidation:
    """Test API validation and error handling"""
    
    async def test_create_client_invalid_email(self, test_client: AsyncClient):
        """Test creating client with invalid email"""
        client_data = {
            "name": "Test Agency",
            "contact_email": "invalid-email",
            "description": "Test description"
        }
        
        response = await test_client.post("/api/v1/clients/", json=client_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_create_client_missing_required_fields(self, test_client: AsyncClient):
        """Test creating client without required fields"""
        client_data = {
            "description": "Test description"
            # Missing name and contact_email
        }
        
        response = await test_client.post("/api/v1/clients/", json=client_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_create_website_invalid_domain(self, test_client: AsyncClient, sample_client):
        """Test creating website with invalid domain"""
        website_data = {
            "client_id": sample_client.id,
            "domain": "not-a-valid-url",
            "name": "Test Website"
        }
        
        response = await test_client.post("/api/v1/websites/", json=website_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    async def test_create_website_nonexistent_client(self, test_client: AsyncClient):
        """Test creating website with non-existent client ID"""
        website_data = {
            "client_id": 99999,  # Non-existent client
            "domain": "https://example.com",
            "name": "Test Website"
        }
        
        response = await test_client.post("/api/v1/websites/", json=website_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY or response.status_code == status.HTTP_400_BAD_REQUEST
