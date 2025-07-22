# a2pbr (Audio to PBR)

This API converts audio files to PBR (Physically Based Rendering) material parameters using FAL's Whisper API.

## Endpoints

### Health Check
- `GET /health`

### Audio to PBR
- `POST /a2pbr`
  - Accepts: multipart/form-data with fields:
    - `file`: audio file (wav, mp3, etc.)
    - `uid`: unique identifier
    - `language`: language code (e.g., 'en')
  - Returns: JSON with PBR parameters and transcription

### Status
- `GET /status/{uid}`
  - Returns: status and PBR parameters for the given UID

## Example Usage

```python
import requests

url = "http://localhost:8000/a2pbr"
files = {"file": open("audio.wav", "rb")}
data = {"uid": "test_123", "language": "en"}
response = requests.post(url, files=files, data=data)
print(response.json())
```

## Running the Service

Build and run with Docker:

```bash
docker build -t a2pbr .
docker run --rm -d -p 8000:8000 --env FAL_KEY=$FAL_KEY --name a2pbr a2pbr
```

## Testing

Run the test scripts:

```bash
python test_api.py
python test_concurrent.py
```

## Notes
- The `/a2pbr` endpoint replaces the previous `/transcribe` endpoint.
- The service is designed for concurrent requests and background processing.
- See the code for more details on error handling and status tracking. 