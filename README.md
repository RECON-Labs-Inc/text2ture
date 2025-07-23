# Text2Ture API

This API converts text, audio, and images to PBR (Physically Based Rendering) material parameters and 3D mesh objects.

## Endpoints

### Health Check
- `GET /health`

### Audio to PBR (a2pbr)
- `POST /a2pbr`
  - Accepts: multipart/form-data with fields:
    - `text`: transcribed text content
    - `uid`: unique identifier
    - `inference_params`: JSON string with inference parameters (float, int, string)
    - `custom_arg`: JSON string with object selection data (optional)
  - Returns: JSON with processing status and UID

### Status
- `GET /status/{uid}`
  - Returns: status and object files mapping for the given UID

## Example Usage

### Audio to PBR
```python
import requests
import json

url = "http://localhost:8000/a2pbr"
inference_params = {
    "floatParam": 0.5,
    "intParam": 30,
    "stringParam": "default"
}
custom_arg = {
    "Table": 0,
    "Chair1": 0,
    "Chair2": 1,
    "Chair3": 0,
    "Chair4": 0,
    "Carpet": 0,
    "Wall": 0
}

data = {
    "text": "Create a wooden table with a modern design",
    "uid": "test_123",
    "inference_params": json.dumps(inference_params),
    "custom_arg": json.dumps(custom_arg)
}
response = requests.post(url, data=data)
print(response.json())
```

## Running the Service

Build and run with Docker:

```bash
docker build -t text2ture .
docker run --rm -d -p 8000:8000 --env SAVE_FOLDER=/app/output --name text2ture text2ture
```

Or run directly with Python:

```bash
pip install -r requirements.txt
python main.py
```

## Testing

Run the test scripts:

```bash
python test_api.py
python test_concurrent.py
```

## Notes
- The service processes requests asynchronously in the background
- Object files are generated based on the `custom_arg` object selection data
- Status can be checked using the `/status/{uid}` endpoint
- Generated files are served from the `/objects` static endpoint
- See the code for more details on error handling and status tracking. 