# Voice Analytics API 🚀

**AI-powered, async, and persistent audio transcription & sales call review platform.**

---

## ✨ Features
- **Async audio transcription** with Deepgram (multi-language, fast, accurate)
- **Background processing**: Get a request ID instantly, poll for results
- **PostgreSQL persistence**: All requests and results are saved
- **AI Sales Call Review**: Each transcript is reviewed by GPT-4 for actionable feedback
- **Modern FastAPI backend**: Fully async, production-ready
- **Swagger/OpenAPI docs**: Try it live at `/docs`

---

## 🛠️ Quickstart

1. **Clone & Install**
   ```bash
   git clone <your-repo-url>
   cd VoiceAnalytics
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env and add your Deepgram and OpenAI API keys
   # Set your PostgreSQL connection string
   ```

3. **Initialize Database**
   ```bash
   PYTHONPATH=. python3 svc/db_init.py
   ```

4. **Run the API**
   ```bash
   python3 main.py
   # or
   uvicorn main:app --reload
   ```

---

## 🔥 How it Works

1. **POST `/api/v1/transcribe`**
   - Upload an audio file (WAV, MP3, etc.)
   - Instantly get a `request_id`
   - Processing happens in the background

2. **GET `/api/v1/status/{request_id}`**
   - Poll this endpoint to check if your transcript & review are ready

3. **GET `/api/v1/result/{request_id}`**
   - Get the full transcript and a detailed, AI-generated review of the sales call

---

## 📑 API Reference & Example Structures

### 1. Transcribe Audio
**Endpoint:** `POST /api/v1/transcribe`

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `audio_file`: The audio file to transcribe (WAV, MP3, M4A, FLAC, OGG, WEBM, MP4)

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
     -F "audio_file=@your_audio.wav"
```

**Response:**
```json
{
  "request_id": "b7e2e2e2-1234-5678-9abc-abcdef123456"
}
```

---

### 2. Check Status
**Endpoint:** `GET /api/v1/status/{request_id}`

**Request:**
- Path parameter: `request_id` (UUID string)

**Example cURL:**
```bash
curl "http://localhost:8000/api/v1/status/b7e2e2e2-1234-5678-9abc-abcdef123456"
```

**Response:**
```json
{
  "request_id": "b7e2e2e2-1234-5678-9abc-abcdef123456",
  "status": "pending" // or "processing", "done", "error"
}
```

---

### 3. Get Result
**Endpoint:** `GET /api/v1/result/{request_id}`

**Request:**
- Path parameter: `request_id` (UUID string)

**Example cURL:**
```bash
curl "http://localhost:8000/api/v1/result/b7e2e2e2-1234-5678-9abc-abcdef123456"
```

**Response (Success):**
```json
{
  "request_id": "b7e2e2e2-1234-5678-9abc-abcdef123456",
  "result": {
    "review": "Start of the conversation: 4/5... (AI-generated feedback here)"
  }
}
```

**Response (Error):**
```json
{
  "request_id": "b7e2e2e2-1234-5678-9abc-abcdef123456",
  "error": "Transcription failed: ..."
}
```

**Response (Still Processing):**
```json
{
  "request_id": "b7e2e2e2-1234-5678-9abc-abcdef123456",
  "status": "pending"
}
```

---

## 🧠 Example: Sales Call Review

The API uses GPT-4 to review your sales call transcript on:
- Start of the conversation
- Pitching of the product
- Understanding the customer’s problem
- Collecting required information
- Ending the call

For each, you get:
- A rating (1-5)
- What was done well
- Suggestions for improvement

---

## 📦 Project Structure

```
VoiceAnalytics/
├── main.py                  # FastAPI app entrypoint
├── requirements.txt         # Dependencies
├── env.example              # Environment variable template
├── svc/
│   ├── db.py                # Async DB setup
│   ├── db_init.py           # DB migration script
│   ├── models.py            # SQLAlchemy models
│   ├── analyse_file_svc.py  # Deepgram & OpenAI logic
├── controller/
│   └── analyse_file.py      # API endpoints
└── README.md
```

---

## 🌍 API Demo (with `curl`)

**Transcribe & Review:**
```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
     -F "audio_file=@your_audio.wav"
# Response: { "request_id": "..." }
```

**Check Status:**
```bash
curl "http://localhost:8000/api/v1/status/<request_id>"
```

**Get Result:**
```bash
curl "http://localhost:8000/api/v1/result/<request_id>"
```

---

## 💡 Why VoiceAnalytics?
- **Async & Scalable**: Never wait for a long upload to finish
- **Persistent**: All your requests and results are saved
- **AI Insights**: Get actionable, human-like feedback on every sales call
- **OpenAPI Docs**: Test and explore at `/docs`

---

## 📝 License
MIT 