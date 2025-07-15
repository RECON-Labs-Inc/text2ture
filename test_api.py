#!/usr/bin/env python3
"""
Test script for the Text2Ture API
"""

import asyncio
import httpx
import json
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_UID = "test_123"
TEST_AUDIO_FILE = "trump_audio.wav"  # Use the local audio file

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
        
        # Test transcription endpoint with file upload
        print(f"\n2. Testing transcription endpoint...")
        print(f"   UID: {TEST_UID}")
        print(f"   Audio file: {TEST_AUDIO_FILE}")
        
        # Check if test audio file exists
        if not os.path.exists(TEST_AUDIO_FILE):
            print(f"❌ Test audio file {TEST_AUDIO_FILE} not found!")
            print("   Please make sure you have an audio file to test with.")
            return
        
        try:
            with open(TEST_AUDIO_FILE, "rb") as audio_file:
                files = {"file": (TEST_AUDIO_FILE, audio_file, "audio/wav")}
                data = {"uid": TEST_UID}
                
                response = await client.post(
                    f"{API_BASE_URL}/transcribe",
                    files=files,
                    data=data,
                    timeout=120.0
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Transcription successful: {response.status_code}")
                print(f"   Status: {result.get('status')}")
                print(f"   Transcription: {result.get('transcription', 'N/A')}")
                print(f"   File path: {result.get('file_path')}")
            else:
                print(f"❌ Transcription failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Transcription request failed: {e}")
        
        # Test status endpoint
        print(f"\n3. Testing status endpoint...")
        try:
            response = await client.get(f"{API_BASE_URL}/status/{TEST_UID}")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Status check successful: {response.status_code}")
                print(f"   UID: {status.get('uid')}")
                print(f"   Status: {status.get('status')}")
                print(f"   File exists: {status.get('file_exists')}")
                pbr_params = status.get('pbr_parameters')
                if pbr_params:
                    print(f"   PBR Parameters:")
                    for key, value in pbr_params.items():
                        print(f"     {key}: {value}")
                else:
                    print(f"   PBR Parameters: None")
            else:
                print(f"❌ Status check failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Status check failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting API tests...")
    print("Make sure the server is running on http://localhost:8000")
    print("Set your FAL_API_KEY environment variable before running tests")
    print(f"Make sure you have the test audio file: {TEST_AUDIO_FILE}")
    print("-" * 50)
    
    asyncio.run(test_api())
    
    print("\n" + "-" * 50)
    print("🎉 Tests completed!") 