#!/usr/bin/env python3
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        try:
            # Test health
            response = await client.get("http://localhost:8000/health")
            print(f"Health: {response.status_code} - {response.json()}")
            
            # Test root
            response = await client.get("http://localhost:8000/")
            print(f"Root: {response.status_code} - {response.json()}")
            
            # Test clients
            response = await client.get("http://localhost:8000/api/v1/clients/")
            print(f"Clients: {response.status_code} - {len(response.json())} found")
            
            # Test websites
            response = await client.get("http://localhost:8000/api/v1/websites/")
            print(f"Websites: {response.status_code} - {len(response.json())} found")
            
            print("✅ All basic tests passed!")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())