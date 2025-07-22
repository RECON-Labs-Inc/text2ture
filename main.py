import os
import asyncio
import aiofiles
import json
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from pydantic import BaseModel
import httpx
from typing import Optional, Dict, Any
import logging
from app import process
from fastapi.staticfiles import StaticFiles


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Text2Ture API", description="Text to PBR parameters")

# Environment variables
SAVE_FOLDER = os.getenv("SAVE_FOLDER", "./output")

# Ensure save folder exists
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Mount static files for serving object files
app.mount("/objects", StaticFiles(directory=SAVE_FOLDER), name="objects")

class StatusResponse(BaseModel):
    uid: str
    status: str
    object_files: Optional[Dict[str, str]] = None

@app.get("/")
async def root():
    return {"message": "Text2Ture API is running"}

@app.post("/a2pbr", response_model=dict)
async def a2pbr(text: str = Form(...), uid: str = Form(...), sd_inference_steps: int = Form(30), pre_prompt: str = Form(""), post_prompt: str = Form("")):
    """
    Convert transcribed text to PBR parameters
    """
    try:
        logger.info(f"Received text request for UID: {uid}")
        logger.info(f"Text: {text[:100]}")
        logger.info(f"Parameters: sd_inference_steps={sd_inference_steps}, pre_prompt={pre_prompt}, post_prompt={post_prompt}")
        
        # Create transcription result structure similar to what FAL would return
        transcription_result = {
            "text": text,
            "uid": uid,
            "sd_inference_steps": sd_inference_steps,
            "pre_prompt": pre_prompt,
            "post_prompt": post_prompt
        }
        
        # Start processing in background task
        asyncio.create_task(process(transcription_result, uid))
        
        # Return immediately
        return {
            "uid": uid,
            "status": "processing",
            "text": text,
            "message": "Received. Processing started in background."
        }
            
    except Exception as e:
        logger.error(f"Error processing text for UID {uid}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/status/{uid}", response_model=StatusResponse)
async def get_status(uid: str):
    """
    Check the status of a text processing request by UID
    """
    uid_dir = os.path.join(SAVE_FOLDER, uid)
    file_path = os.path.join(uid_dir, f"{uid}.json")
    error_file_path = os.path.join(uid_dir, f"{uid}_error.json")
    completed_exists = os.path.exists(file_path)
    error_exists = os.path.exists(error_file_path)
    

    
    if error_exists:
        status = "error"
        object_files = None
        try:
            async with aiofiles.open(error_file_path, 'r') as f:
                content = await f.read()
                error_info = json.loads(content)
                logger.error(f"Error for UID {uid}: {error_info.get('error', 'Unknown error')}")
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading error file {error_file_path}: {e}")
    elif completed_exists:
        status = "completed"
        object_files = None
        try:
            async with aiofiles.open(file_path, 'r') as f:
                content = await f.read()
                object_files = json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
    else:
        status = "processing"
        object_files = None
    
    return StatusResponse(
        uid=uid,
        status=status,
        object_files=object_files
    )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "save_folder": SAVE_FOLDER
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 