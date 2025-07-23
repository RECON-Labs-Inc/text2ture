#!/usr/bin/env python3
"""
Test script for the Text2Ture API (updated for new backend)
"""

import asyncio
import httpx
import json
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_UID = "test_123"

def get_inference_params():
    return {
        "floatParam": 0.5,
        "intParam": 30,
        "stringParam": "default"
    }

def get_custom_arg():
    return {
        "Table": 0,
        "Chair1": 0,
        "Chair2": 1,
        "Chair3": 0,
        "Chair4": 0,
        "Carpet": 0,
        "Wall": 0
    }

async def test_api():
    async with httpx.AsyncClient() as client:
        print("🧪 Testing Text2Ture API...")
        
        # Test health endpoint
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{API_BASE_URL}/health")
            print(f"✅ Health check: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return
        
        # Test a2pbr endpoint with text, inference_params, and custom_arg
        print(f"\n2. Testing a2pbr endpoint...")
        print(f"   UID: {TEST_UID}")
        
        data = {
            "text": "Create a wooden table with a modern design",
            "uid": TEST_UID,
            "inference_params": json.dumps(get_inference_params()),
            "custom_arg": json.dumps(get_custom_arg())
        }
        try:
            response = await client.post(
                f"{API_BASE_URL}/a2pbr",
                data=data,
                timeout=120.0
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ a2pbr successful: {response.status_code}")
                print(f"   Status: {result.get('status')}")
                print(f"   UID: {result.get('uid')}")
                print(f"   Message: {result.get('message')}")
            else:
                print(f"❌ a2pbr failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ a2pbr request failed: {e}")
        
        # Test status endpoint
        print(f"\n3. Testing status endpoint...")
        try:
            response = await client.get(f"{API_BASE_URL}/status/{TEST_UID}")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Status check successful: {response.status_code}")
                print(f"   UID: {status.get('uid')}")
                print(f"   Status: {status.get('status')}")
                object_files = status.get('object_files')
                if object_files:
                    print(f"   Object Files:")
                    for key, value in object_files.items():
                        print(f"     {key}: {value}")
                else:
                    print(f"   Object Files: None")
            else:
                print(f"❌ Status check failed: {response.status_code}")
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"❌ Status check failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting API tests...")
    print("Make sure the server is running on http://localhost:8000")
    print("-" * 50)
    
    asyncio.run(test_api())
    
    print("\n" + "-" * 50)
    print("🎉 Tests completed!") 