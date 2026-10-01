# GERONIMO Backend API Setup Guide

This guide explains how to connect the GERONIMO website to a small backend service that can power the AI dashboard, task execution flow, and PC control features.

## Overview

The frontend pages (`index.html`, `dashboard.html`, `tasks.html`, `pc-control.html`, and `settings.html`) are static HTML pages. To make them intelligent, they can talk to a backend API that:

- authenticates users
- stores task history and execution logs
- routes requests to Gemini or another AI model
- manages permissions and usage policies
- exposes actions for app control, file actions, and automation

## Recommended Backend

Use a Python FastAPI service.

### Why FastAPI?

- simple REST API design
- built-in validation with Pydantic
- clean async support
- easy to deploy on Render, Railway, Fly.io, or a VPS
- works well with Firebase and Gemini

## Project Structure

```text
GERONIMO/
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── tasks.html
│   ├── pc-control.html
│   ├── settings.html
│   └── algorithms.html
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── auth.py
│   ├── ai.py
│   ├── tasks.py
│   └── requirements.txt
├── .env
├── README.md
└── .gitignore
```

## Backend API Routes

Recommended endpoints:

### Authentication

- POST `/api/auth/login`
- POST `/api/auth/register`
- POST `/api/auth/logout`
- GET `/api/auth/session`

### AI Tasks

- POST `/api/ai/chat`
- POST `/api/ai/plan`
- POST `/api/ai/execute`
- GET `/api/ai/history`

### Tasks

- GET `/api/tasks`
- GET `/api/tasks/{id}`
- POST `/api/tasks`
- PATCH `/api/tasks/{id}`
- DELETE `/api/tasks/{id}`

### PC Control

- GET `/api/system/health`
- GET `/api/system/apps`
- POST `/api/system/app/open`
- POST `/api/system/app/close`
- POST `/api/system/action`

### Settings

- GET `/api/settings`
- PUT `/api/settings`

## Example FastAPI Server

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="GERONIMO API")

@app.get("/health")
def health():
    return {"status": "ok", "service": "GERONIMO"}

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.post("/api/ai/chat")
def chat(request: ChatRequest):
    return {
        "reply": f"AI received: {request.message}",
        "user_id": request.user_id,
        "status": "queued"
    }
```

## Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_key
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
JWT_SECRET=your-super-secret-key
ALLOWED_ORIGINS=https://pintoira.github.io, http://localhost:8000
```

## Dependencies

Create `backend/requirements.txt`:

```text
fastapi==0.115.0
uvicorn==0.30.6
pydantic==2.9.2
python-dotenv==1.0.1
google-genai==1.0.0
firebase-admin==6.5.0
python-jose[cryptography]==3.4.0
httpx==0.27.2
```

## Firebase Integration

Use Firebase Auth for sign-in and secure sessions.

Examples:

- frontend signs in with Firebase
- frontend sends Firebase ID token to backend
- backend verifies token before processing requests

This keeps user identity secure and makes it easy to restrict dangerous actions.

## Gemini Integration

Use Gemini to handle:

- natural-language interpretation
- task planning
- summarizing user requests
- generating step-by-step instructions

Example AI logic:

1. user says: "Open Excel and create a Q3 report"
2. backend sends prompt to Gemini
3. Gemini returns a structured task plan
4. backend stores plan in task queue
5. frontend shows progress in `tasks.html`

## Safety Rules

Protect windows and PC actions with permission checks:

- ask user approval before deleting files
- ask approval before changing system settings
- log every command
- disable certain actions by default
- restrict permissions per user profile

## Deployment Tips

### Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Production

Deploy to a service such as:

- Render
- Railway
- Fly.io
- DigitalOcean
- Azure App Service

Then point your frontend to the cloud API URL.

## Connecting Frontend to Backend

Use JavaScript `fetch()` from the static pages:

```javascript
const res = await fetch('https://your-api-url/api/ai/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    message: 'Open Excel and prepare my report',
    user_id: 'user-123'
  })
});
```

## Best Next Step

For your GERONIMO project, the most useful first backend feature is:

- `POST /api/ai/chat` for natural-language command handling
- `GET /api/tasks` for task status tracking
- `POST /api/system/action` for safe item execution

This gives you a strong base for building the actual AI assistant behind the website.

## Recommended Next Milestones

1. Set up FastAPI with Firebase authentication
2. Connect Gemini to analyze user commands
3. Add task storage and status tracking
4. Add permission enforcement for PC actions
5. Connect `dashboard.html` to real API calls

This is the cleanest architecture for turning GERONIMO from a static demo into a real AI control system.
