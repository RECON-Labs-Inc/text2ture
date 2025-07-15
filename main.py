import os
import asyncio
import aiofiles
import json
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
import httpx
from typing import Optional, Dict, Any
import logging
import fal_client
from app import process


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text2Ture API", description="Audio to PBR parameters")

# Environment variables
FAL_API_KEY = os.getenv("FAL_KEY")
SAVE_FOLDER = os.getenv("SAVE_FOLDER", "./output")

# Ensure save folder exists
os.makedirs(SAVE_FOLDER, exist_ok=True)

class StatusResponse(BaseModel):
    uid: str
    status: str
    file_exists: bool
    pbr_parameters: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "Text2Ture API is running"}

@app.post("/transcribe", response_model=dict)
async def transcribe_audio(file: UploadFile = File(...), uid: str = Form(...), language: str = Form(...)):
    """
    Transcribe audio using FAL's Whisper API
    """
    if not FAL_API_KEY:
        raise HTTPException(status_code=500, detail="FAL_API_KEY not configured")
    
    try:
        os.makedirs("/data", exist_ok=True)
        
        # Save uploaded file temporarily
        file_path = f"/data/audio_{uid}.wav"


        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Saved uploaded file to {file_path} for UID: {uid}")

        # Upload file to FAL
        url = await fal_client.upload_file_async(file_path)
        
        logger.info(f"URL {url} for UID: {uid}")
        # Call FAL's Whisper API with the uploaded file
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://fal.run/fal-ai/whisper",
                headers={
                    "Authorization": f"Key {FAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "audio_url": url,
                    "language": language
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"FAL API error: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="FAL API error")
            
            transcription_result = response.json()
            logger.info(f"Transcription completed for UID: {uid}")
            
            # Clean up temporary file
            os.remove(file_path)
            
            # Start processing in background task
            asyncio.create_task(process(transcription_result, uid))
            
            # Return immediately with transcription result
            return {
                "uid": uid,
                "status": "processing",
                "transcription": transcription_result.get("text", ""),
                "message": "Transcription completed. Processing started in background."
            }
            
    except httpx.TimeoutException:
        logger.error(f"Timeout calling FAL API for UID: {uid}")
        raise HTTPException(status_code=408, detail="Request timeout")
    except Exception as e:
        logger.error(f"Error processing transcription for UID {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/status/{uid}", response_model=StatusResponse)
async def get_status(uid: str):
    """
    Check the status of a transcription request by UID
    """
    file_path = os.path.join(SAVE_FOLDER, f"{uid}.json")
    error_file_path = os.path.join(SAVE_FOLDER, f"{uid}_error.json")
    
    file_exists = os.path.exists(file_path)
    error_exists = os.path.exists(error_file_path)
    
    if error_exists:
        status = "error"
        pbr_parameters = None
        try:
            async with aiofiles.open(error_file_path, 'r') as f:
                content = await f.read()
                error_info = json.loads(content)
                logger.error(f"Error for UID {uid}: {error_info.get('error', 'Unknown error')}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading error file {error_file_path}: {e}")
    elif file_exists:
        status = "completed"
        pbr_parameters = None
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                pbr_parameters = json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            # If we can't read the JSON, still return that file exists but with None parameters
    else:
        status = "processing"
        pbr_parameters = None
    
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