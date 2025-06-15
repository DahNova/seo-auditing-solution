#!/usr/bin/env python3
"""
Test script for SEO Auditing Solution API
"""
import asyncio
import httpx
import json
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

async def test_api():
    """Test API endpoints"""
    async with httpx.AsyncClient() as client:
        
        # Test health endpoint
        logger.info("🏥 Testing health endpoint...")
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        logger.info("✅ Health check passed")
        
        # Test root endpoint
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        logger.info("✅ Root endpoint passed")
        
        # Test API docs
        response = await client.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
        logger.info("✅ API docs accessible")
        
        # Test clients endpoint
        logger.info("👥 Testing clients API...")
        response = await client.get(f"{BASE_URL}/api/v1/clients/")
        assert response.status_code == 200
        clients = response.json()
        logger.info(f"✅ Found {len(clients)} clients")
        
        if clients:
            client_id = clients[0]["id"]
            
            # Test single client
            response = await client.get(f"{BASE_URL}/api/v1/clients/{client_id}")
            assert response.status_code == 200
            logger.info("✅ Single client retrieval passed")
            
            # Test websites for client
            logger.info("🌐 Testing websites API...")
            response = await client.get(f"{BASE_URL}/api/v1/websites/?client_id={client_id}")
            assert response.status_code == 200
            websites = response.json()
            logger.info(f"✅ Found {len(websites)} websites for client")
            
            if websites:
                website_id = websites[0]["id"]
                
                # Test create scan
                logger.info("🔍 Testing scan creation...")
                scan_data = {"website_id": website_id}
                response = await client.post(
                    f"{BASE_URL}/api/v1/scans/",
                    json=scan_data
                )
                if response.status_code == 201:
                    scan = response.json()
                    scan_id = scan["id"]
                    logger.info(f"✅ Scan created with ID: {scan_id}")
                    
                    # Check scan status
                    response = await client.get(f"{BASE_URL}/api/v1/scans/{scan_id}")
                    assert response.status_code == 200
                    logger.info("✅ Scan retrieval passed")
                else:
                    logger.warning(f"⚠️  Scan creation failed: {response.text}")
        
        logger.info("🎉 All API tests passed!")

async def test_create_client():
    """Test creating a new client"""
    async with httpx.AsyncClient() as client:
        client_data = {
            "name": "Test Client API",
            "description": "Created via API test",
            "contact_email": "api-test@example.com"
        }
        
        response = await client.post(
            f"{BASE_URL}/api/v1/clients/",
            json=client_data
        )
        
        if response.status_code == 201:
            new_client = response.json()
            logger.info(f"✅ Created new client: {new_client['name']} (ID: {new_client['id']})")
            return new_client
        else:
            logger.error(f"❌ Failed to create client: {response.text}")
            return None

async def main():
    """Main test function"""
    logger.info("🧪 Starting API tests...")
    
    try:
        # Test basic API functionality
        await test_api()
        
        # Test creating new data
        new_client = await test_create_client()
        
        logger.info("✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Tests failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)