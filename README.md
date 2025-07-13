# Voice Analytics API

A FastAPI application for voice analytics with audio transcription capabilities using Deepgram API.

## Features

- Audio file transcription using Deepgram API
- Support for multiple audio formats (MP3, WAV, M4A, FLAC, OGG, WEBM, MP4)
- RESTful API endpoints
- Automatic API documentation with Swagger UI
- File upload validation
- Detailed transcription results with timestamps and confidence scores

## Prerequisites

- Python 3.8+
- Deepgram API key (get one from [Deepgram Console](https://console.deepgram.com/))

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env and add your Deepgram API key
   # You can also customize HOST, PORT, and LOG_LEVEL
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /api/v1/transcribe` - Transcribe audio file

## API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage

### Transcribe an audio file
```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
     -H "Content-Type: multipart/form-data" \
     -F "audio_file=@path/to/your/audio.mp3"
```

### Using Python requests
```python
import requests

url = "http://localhost:8000/api/v1/transcribe"
files = {"audio_file": open("audio.mp3", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Response Format

The transcription endpoint returns a detailed response including:

- **Metadata**: File information, duration, model used
- **Results**: Complete transcript with word-level timestamps
- **Confidence scores**: Per-word and overall confidence
- **Paragraphs**: Structured text with sentence boundaries

Example response structure:
```json
{
  "metadata": {
    "request_id": "2479c8c8-8185-40ac-9ac6-f0874419f793",
    "duration": 25.933313,
    "models": ["30089e05-99d1-4376-b32e-c263170674af"]
  },
  "results": {
    "channels": [
      {
        "alternatives": [
          {
            "transcript": "Complete transcript text...",
            "confidence": 0.99902344,
            "words": [...],
            "paragraphs": {...}
          }
        ]
      }
    ]
  }
}
```

## Project Structure

```
VoiceAnalytics/
├── main.py                    # Main FastAPI application
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
├── controller/
│   └── analyse_file.py       # Audio transcription controller
├── svc/
│   └── analyse_file_svc.py   # Deepgram service layer
└── README.md                 # This file
```

## Supported Audio Formats

- MP3
- WAV
- M4A
- FLAC
- OGG
- WEBM
- MP4

## File Size Limits

- Maximum file size: 100MB
- For larger files, consider chunking or streaming

## Development

For production deployment, consider:
- Adding authentication and authorization
- Implementing rate limiting
- Adding request logging
- Setting up monitoring and alerting
- Adding comprehensive error handling
- Implementing file storage (S3, etc.)
- Adding caching for repeated transcriptions 