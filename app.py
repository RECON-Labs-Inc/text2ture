import os
import asyncio
import aiofiles
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def process(input_data: Dict[str, Any], uid: str):
    """
    Background processing function for transcription results
    This runs asynchronously and doesn't block the main API
    """
    try:
        logger.info(f"Starting background processing for UID: {uid}")
        
        # Get the transcription text and additional parameters
        transcription_text = input_data.get("text", "")
        inference_params = input_data.get("inference_params", {})
        custom_arg = input_data.get("custom_arg", None)
        
        logger.info(f"Processing transcription: {transcription_text[:100]}")
        logger.info(f"Parameters: inference_params={inference_params}, custom_arg={custom_arg}")
        
        await asyncio.sleep(2)  # Simulate processing

        # Prepare output directory for this UID
        save_folder = os.getenv("SAVE_FOLDER", "./output")
        uid_dir = os.path.join(save_folder, uid)
        os.makedirs(uid_dir, exist_ok=True)

        # Parse custom_arg to get selected objects
        all_objects = []
        if custom_arg:
            try:
                custom_arg_dict = json.loads(custom_arg)
                # Get all objects from the custom_arg
                all_objects = list(custom_arg_dict.keys())
                logger.info(f"All objects: {all_objects}")
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing custom_arg JSON: {e}")
                all_objects = []

        # Build the mapping of object names to URLs
        object_files = {}
        sample_image_path = os.path.join(os.path.dirname(__file__), "sample_image.jpg")
        for obj_name in all_objects:
            filename = f"{obj_name}.jpg"
            file_path = os.path.join(uid_dir, filename)
            # Copy the sample image as the dummy image
            try:
                async with aiofiles.open(sample_image_path, 'rb') as src, aiofiles.open(file_path, 'wb') as dst:
                    content = await src.read()
                    await dst.write(content)
            except Exception as e:
                logger.error(f"Error copying sample image for {obj_name}: {e}")
            object_files[obj_name] = f"/objects/{uid}/{filename}"

        # Save the mapping as the result JSON file (this is the completion flag)
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