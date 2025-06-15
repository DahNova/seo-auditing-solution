#!/usr/bin/env python3
import httpx
import asyncio
import json

async def test_scan_creation():
    async with httpx.AsyncClient() as client:
        try:
            # Get websites
            response = await client.get("http://localhost:8000/api/v1/websites/")
            websites = response.json()
            print(f"Found {len(websites)} websites")
            
            if websites:
                website_id = websites[0]["id"]
                print(f"Testing scan creation for website ID: {website_id}")
                
                # Create scan
                scan_data = {"website_id": website_id}
                response = await client.post(
                    "http://localhost:8000/api/v1/scans/",
                    json=scan_data
                )
                
                if response.status_code == 201:
                    scan = response.json()
                    print(f"✅ Scan created successfully!")
                    print(f"   - Scan ID: {scan['id']}")
                    print(f"   - Status: {scan['status']}")
                    print(f"   - Website ID: {scan['website_id']}")
                    
                    # Test scan retrieval
                    scan_id = scan['id']
                    response = await client.get(f"http://localhost:8000/api/v1/scans/{scan_id}")
                    if response.status_code == 200:
                        print("✅ Scan retrieval successful")
                    
                    # Test scan listing
                    response = await client.get("http://localhost:8000/api/v1/scans/")
                    scans = response.json()
                    print(f"✅ Total scans in system: {len(scans)}")
                    
                else:
                    print(f"❌ Scan creation failed: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_scan_creation())