import os
import asyncio
import aiofiles
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text2Ture API", description="Audio to PBR parameters")

# Environment variables
FAL_API_KEY = os.getenv("FAL_KEY")
SAVE_FOLDER = os.getenv("SAVE_FOLDER", "./output")

# Ensure save folder exists
os.makedirs(SAVE_FOLDER, exist_ok=True)

class TranscriptionRequest(BaseModel):
    uid: str
    audio_url: str

class StatusResponse(BaseModel):
    uid: str
    status: str
    file_exists: bool
    pbr_parameters: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "Text2Ture API is running"}

@app.post("/transcribe", response_model=dict)
async def transcribe_audio(request: TranscriptionRequest):
    """
    Transcribe audio using FAL's Whisper API
    """
    if not FAL_API_KEY:
        raise HTTPException(status_code=500, detail="FAL_API_KEY not configured")
    
    try:
        # Call FAL's Whisper API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://fal.run/fal-ai/whisper",
                headers={
                    "Authorization": f"Key {FAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "audio_url": request.audio_url
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"FAL API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="FAL API error")
            
            transcription_result = response.json()
            logger.info(f"Transcription completed for UID: {request.uid}")
            
            # Wait for a few seconds (placeholder for future processing)
            await asyncio.sleep(3)
            
            # Save PBR material parameters to a JSON file with the UID as filename
            # This is a placeholder - you can replace this with your actual processing logic
            pbr_parameters = {
                "albedo": [0.8, 0.2, 0.1],
                "roughness": 0.3,
                "metallic": 0.1,
                "normal_strength": 1.0,
                "emissive": [0.0, 0.0, 0.0],
                "ao_strength": 1.0
            }
            file_path = os.path.join(SAVE_FOLDER, f"{request.uid}.json")
            
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(json.dumps(pbr_parameters, indent=2))
            
            logger.info(f"Saved PBR parameters to {file_path}")
            
            return {
                "uid": request.uid,
                "status": "completed",
                "transcription": transcription_result.get("text", ""),
                "file_path": file_path,
                "pbr_parameters": pbr_parameters
            }
            
    except httpx.TimeoutException:
        logger.error(f"Timeout calling FAL API for UID: {request.uid}")
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        logger.error(f"Error processing transcription for UID {request.uid}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/status/{uid}", response_model=StatusResponse)
async def get_status(uid: str):
    """
    Check the status of a transcription request by UID
    """
    file_path = os.path.join(SAVE_FOLDER, f"{uid}.json")
    file_exists = os.path.exists(file_path)
    
    status = "completed" if file_exists else "not_found"
    pbr_parameters = None
    
    if file_exists:
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                pbr_parameters = json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            # If we can't read the JSON, still return that file exists but with None parameters
    
    return StatusResponse(
        uid=uid,
        status=status,
        file_exists=file_exists,
        pbr_parameters=pbr_parameters
    )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    print("FAL_API_KEY")
    print(FAL_API_KEY)
    return {
        "status": "healthy",
        "fal_api_key_configured": bool(FAL_API_KEY),
        "save_folder": SAVE_FOLDER
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 