#!/usr/bin/env python3
"""
Test script to demonstrate concurrent processing capability
"""

import asyncio
import httpx
import json
import os
import time

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_AUDIO_FILE = "/home/sergio/generative3d/trump_audio.wav"

async def submit_transcription(client, uid, language="en"):
    """Submit a transcription request"""
    try:
        with open(TEST_AUDIO_FILE, "rb") as audio_file:
            files = {"file": (TEST_AUDIO_FILE, audio_file, "audio/wav")}
            data = {"uid": uid, "language": language}
            
            response = await client.post(
                f"{API_BASE_URL}/a2pbr",
                files=files,
                data=data,
                timeout=120.0
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Request {uid}: {result.get('status')} - {result.get('transcription', 'N/A')[:50]}...")
            return result
        else:
            print(f"❌ Request {uid} failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Request {uid} failed: {e}")
        return None

async def check_status(client, uid):
    """Check status of a request"""
    try:
        response = await client.get(f"{API_BASE_URL}/status/{uid}")
        if response.status_code == 200:
            status = response.json()
            return status.get('status')
        else:
            return "unknown"
    except Exception as e:
        return "error"

async def test_concurrent_processing():
    """Test multiple simultaneous requests"""
    async with httpx.AsyncClient() as client:
        print("🚀 Testing concurrent processing...")
        print(f"Audio file: {TEST_AUDIO_FILE}")
        
        if not os.path.exists(TEST_AUDIO_FILE):
            print(f"❌ Test audio file {TEST_AUDIO_FILE} not found!")
            return
        
        # Submit multiple requests simultaneously
        uids = [f"concurrent_test_{i}" for i in range(1, 6)]
        print(f"\n📤 Submitting {len(uids)} requests simultaneously...")
        
        start_time = time.time()
        
        # Submit all requests concurrently
        tasks = [submit_transcription(client, uid) for uid in uids]
        results = await asyncio.gather(*tasks)
        
        submission_time = time.time() - start_time
        print(f"\n⏱️  All requests submitted in {submission_time:.2f} seconds")
        
        # Monitor status of all requests
        print(f"\n📊 Monitoring processing status...")
        completed = set()
        max_wait_time = 60  # Maximum wait time in seconds
        start_monitor = time.time()
        
        while len(completed) < len(uids) and (time.time() - start_monitor) < max_wait_time:
            for uid in uids:
                if uid not in completed:
                    status = await check_status(client, uid)
                    if status in ["completed", "error"]:
                        completed.add(uid)
                        print(f"✅ {uid}: {status}")
                    elif status == "processing":
                        print(f"⏳ {uid}: {status}")
            
            if len(completed) < len(uids):
                await asyncio.sleep(2)  # Wait 2 seconds before checking again
        
        total_time = time.time() - start_time
        print(f"\n🎉 Concurrent processing test completed in {total_time:.2f} seconds")
        print(f"   Completed: {len(completed)}/{len(uids)} requests")

if __name__ == "__main__":
    print("🧪 Starting concurrent processing test...")
    print("Make sure the server is running on http://localhost:8000")
    print("-" * 50)
    
    asyncio.run(test_concurrent_processing())
    
    print("\n" + "-" * 50)
    print("🎉 Concurrent test completed!") 