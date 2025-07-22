import os
import asyncio
import aiofiles
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def process(transcription_result: Dict[str, Any], uid: str):
    """
    Background processing function for transcription results
    This runs asynchronously and doesn't block the main API
    """
    try:
        logger.info(f"Starting background processing for UID: {uid}")
        
        # Get the transcription text and additional parameters
        transcription_text = transcription_result.get("text", "")
        sd_inference_steps = transcription_result.get("sd_inference_steps", 30)
        pre_prompt = transcription_result.get("pre_prompt", "")
        post_prompt = transcription_result.get("post_prompt", "")
        
        logger.info(f"Processing transcription: {transcription_text[:100]}")
        logger.info(f"Parameters: sd_inference_steps={sd_inference_steps}, pre_prompt={pre_prompt}, post_prompt={post_prompt}")
        
        await asyncio.sleep(2)  # Simulate processing

        # Prepare output directory for this UID
        save_folder = os.getenv("SAVE_FOLDER", "./output")
        uid_dir = os.path.join(save_folder, uid)
        os.makedirs(uid_dir, exist_ok=True)

        # Build the mapping of object names to URLs
        object_files = {}
        object_names = ["sofa", "chair", "table", "lamp", "plant"]
        for name in object_names:
            filename = f"{name}.png"
            file_path = os.path.join(uid_dir, filename)
            # Write dummy content
            async with aiofiles.open(file_path, 'w') as f:
                await f.write(f"This is dummy data for {name} of UID {uid}.\n")
            object_files[name] = f"/objects/{uid}/{filename}"

        # Save the mapping as the result JSON file (this is now the completion flag)
        output_file_path = os.path.join(uid_dir, f"{uid}.json")
        async with aiofiles.open(output_file_path, 'w') as f:
            await f.write(json.dumps(object_files, indent=2))

        logger.info(f"Background processing completed for UID: {uid}")
        logger.info(f"Saved object file mapping to {output_file_path}")
        
    except Exception as e:
        logger.error(f"Error in background processing for UID {uid}: {str(e)}")
        # You might want to save error status to a file or database
        save_folder = os.getenv("SAVE_FOLDER", "./output")
        error_file_path = os.path.join(save_folder, f"{uid}_error.json")
        async with aiofiles.open(error_file_path, 'w') as f:
            await f.write(json.dumps({"error": str(e), "uid": uid}, indent=2)) 