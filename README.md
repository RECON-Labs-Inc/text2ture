# Text2Ture API

A FastAPI server that transcribes audio using FAL's Whisper API and generates PBR material parameters.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export FAL_API_KEY="your_fal_api_key_here"
export SAVE_FOLDER="./output"  # Optional, defaults to ./output
```

3. Run the server:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### POST /transcribe
Transcribe audio using FAL's Whisper API.

**Request Body:**
```json
{
  "uid": "unique_identifier_123",
  "audio_url": "https://example.com/audio.mp3"
}
```

**Response:**
```json
{
  "uid": "unique_identifier_123",
  "status": "completed",
  "transcription": "This is the transcribed text...",
  "file_path": "./output/unique_identifier_123.json",
  "pbr_parameters": {
    "albedo": [0.8, 0.2, 0.1],
    "roughness": 0.3,
    "metallic": 0.1,
    "normal_strength": 1.0,
    "emissive": [0.0, 0.0, 0.0],
    "ao_strength": 1.0
  }
}
```

### GET /status/{uid}
Check the status of a transcription request.

**Response:**
```json
{
  "uid": "unique_identifier_123",
  "status": "completed",
  "file_exists": true,
  "pbr_parameters": {
    "albedo": [0.8, 0.2, 0.1],
    "roughness": 0.3,
    "metallic": 0.1,
    "normal_strength": 1.0,
    "emissive": [0.0, 0.0, 0.0],
    "ao_strength": 1.0
  }
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "fal_api_key_configured": true,
  "save_folder": "./output"
}
```

## Environment Variables

- `FAL_API_KEY`: Your FAL API key (required)
- `SAVE_FOLDER`: Directory to save output files (optional, defaults to `./output`)

## Features

1. **Audio Transcription**: Uses FAL's Whisper API to transcribe audio from URLs
2. **PBR Parameter Generation**: Generates PBR material parameters based on audio content
3. **Status Tracking**: Each request is tracked by a unique UID
4. **JSON Output**: Saves PBR parameters to JSON files named with the UID
5. **Async Processing**: Non-blocking API calls with proper error handling
6. **Health Monitoring**: Built-in health check endpoint

## Notes

- The server waits 3 seconds after transcription as a placeholder for future processing
- Currently saves placeholder PBR parameters to JSON files - replace this with your actual processing logic
- All output files are saved in the directory specified by `SAVE_FOLDER` environment variable
- The API includes comprehensive error handling and logging 