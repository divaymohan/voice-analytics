# Voice Analytics API 🚀

**AI-powered, async, and persistent audio transcription & sales call review platform with multi-tenant authentication!**

---

## ✨ Features
- **Async audio transcription** with Deepgram (multi-language, fast, accurate)
- **Background processing**: Get a request ID instantly, poll for results
- **PostgreSQL persistence**: All requests and results are saved
- **AI Sales Call Review**: Each transcript is reviewed by GPT-4 for actionable feedback
- **Multi-tenant authentication**: Users & organizations, JWT-secured
- **Organization onboarding & user invites**: SaaS-ready
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
   # Edit .env and add your Deepgram, OpenAI API keys, and PostgreSQL connection string
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
   - Get the stored transcript and AI-generated review for the given request (no re-processing)

4. **User & Org Auth**
   - Sign up as a user or org owner
   - Log in to get a JWT
   - Org owners can invite users to their org

5. **Transcript Management**
   - Org owners can list all org transcripts (with user info)
   - Users can list their own transcripts
   - Soft delete transcripts (by creator or org owner)

---

## 🧑‍💼 Multi-Tenant Auth & Organization Onboarding

### 1. Sign Up (User or Org Owner)
**POST `/auth/signup`**
```json
{
  "name": "Alice",
  "email": "alice@acme.com",
  "password": "strongpassword",
  "organization_name": "Acme Inc" // Optional: if present, creates org and makes user owner
}
```
**Response:** `{ "message": "Signup successful" }`

### 2. Login
**POST `/auth/login`**
```json
{
  "email": "alice@acme.com",
  "password": "strongpassword"
}
```
**Response:** `{ "access_token": "...", "token_type": "bearer" }`

### 3. Get Current User & Organization
**GET `/auth/me`** (JWT required)
```json
{
  "user": {
    "id": "...",
    "name": "Alice",
    "email": "alice@acme.com",
    "is_org_owner": true,
    "organization_id": "..."
  },
  "organization": {
    "id": "...",
    "name": "Acme Inc",
    "owner_id": "..."
  }
}
```

### 4. Get Organization Info (JWT required)
**GET `/orgs/{org_id}`**
```json
{
  "id": "...",
  "name": "Acme Inc",
  "owner_id": "..."
}
```

### 5. List Org Users (JWT required)
**GET `/orgs/{org_id}/users`**
```json
[
  { "id": "...", "name": "Alice", "email": "alice@acme.com", "is_org_owner": true },
  { "id": "...", "name": "Bob", "email": "bob@acme.com", "is_org_owner": false }
]
```

### 6. Invite User to Organization (Org Owner + JWT required)
**POST `/orgs/{org_id}/invite`**
```json
{
  "name": "Bob",
  "email": "bob@acme.com",
  "password": "anotherpassword"
}
```
**Response:** `{ "message": "User bob@acme.com invited to organization." }`

---

## 📑 API Reference & Example Structures

### Transcribe Audio
**POST `/api/v1/transcribe`**
```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
     -F "audio_file=@your_audio.wav" -H "Authorization: Bearer <token>"
```
**Response:** `{ "request_id": "..." }`

### Check Status
**GET `/api/v1/status/{request_id}`**
```json
{ "request_id": "...", "status": "pending" }
```

### Get Result
**GET `/api/v1/result/{request_id}`**
```json
{ "request_id": "...", "result": { "review": "...AI feedback..." } }
```

### List All Org Transcripts (Org Owner)
**GET `/api/v1/org/{org_id}/transcripts`**
```json
[
  {
    "request_id": "...",
    "filename": "call1.wav",
    "status": "done",
    "created_at": "2024-06-10T12:00:00Z",
    "user": {
      "id": "...",
      "name": "Alice",
      "email": "alice@acme.com"
    }
  },
  ...
]
```

### List My Transcripts
**GET `/api/v1/user/transcripts`**
```json
[
  {
    "request_id": "...",
    "filename": "call1.wav",
    "status": "done",
    "created_at": "2024-06-10T12:00:00Z"
  },
  ...
]
```

### Soft Delete Transcript
**DELETE `/api/v1/transcript/{request_id}`**
- Only the creator or org owner can delete.
- Sets status to `"deleted"` (soft delete).
```json
{ "message": "Transcript deleted (soft)" }
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
│   ├── auth_utils.py        # Auth/JWT/password utils
├── controller/
│   ├── analyse_file.py      # Audio endpoints
│   ├── auth.py              # Auth endpoints
│   └── org.py               # Org endpoints
└── README.md
```

---

## 🌍 API Demo (with `curl`)

**Transcribe & Review:**
```bash
curl -X POST "http://localhost:8000/api/v1/transcribe" \
     -F "audio_file=@your_audio.wav" -H "Authorization: Bearer <token>"
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

**List Org Transcripts:**
```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/org/<org_id>/transcripts"
```

**List My Transcripts:**
```bash
curl -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/user/transcripts"
```

**Soft Delete Transcript:**
```bash
curl -X DELETE -H "Authorization: Bearer <token>" "http://localhost:8000/api/v1/transcript/<request_id>"
```

---

## 💡 Why VoiceAnalytics?
- **Async & Scalable**: Never wait for a long upload to finish
- **Persistent**: All your requests and results are saved
- **AI Insights**: Get actionable, human-like feedback on every sales call
- **Multi-tenant**: SaaS-ready for teams and organizations
- **OpenAPI Docs**: Test and explore at `/docs`

---

## 📝 License
MIT 