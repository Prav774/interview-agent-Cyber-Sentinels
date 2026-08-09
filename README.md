# AI Interview Agent

An AI-powered adaptive technical interview platform built for
VibeCodathon. The system uses a candidate's learning context to conduct
a conversational technical interview, generate adaptive follow-up
questions, and produce structured final feedback.

## Live Demo

**Frontend:**\
https://interview-agent-cyber-sentinels-82frv1jih-prav774s-projects.vercel.app

**Backend API:**\
https://interview-agent-cyber-sentinels.onrender.com

**API Documentation (Swagger):**\
https://interview-agent-cyber-sentinels.onrender.com/docs

**Health Check:**\
https://interview-agent-cyber-sentinels.onrender.com/health

## Repository Structure

``` text
interview-agent-Cyber-Sentinels/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── services/
│   │   └── ...
│   ├── requirements.txt
│   └── test_*.py
├── data/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
├── .gitignore
└── README.md
```

## What the Project Does

The AI Interview Agent conducts a personalized technical interview
rather than presenting a fixed list of questions.

``` text
Candidate Profile
       ↓
Interview Context
       ↓
Initial Technical Question
       ↓
Candidate Answer
       ↓
Context + Previous Conversation
       ↓
Adaptive Follow-up
       ↓
8+ Questions / 4+ Curriculum Days
       ↓
Final Evaluation
       ↓
Summary + Strengths + Gaps + Next Steps
```

## Key Features

-   Personalized technical interview flow
-   Session-based conversation state using `sessionId`
-   Adaptive follow-up questions
-   Candidate learning/curriculum context
-   Minimum 8-question interview
-   Coverage of at least 4 curriculum days before completion
-   Structured final feedback
-   FastAPI backend
-   React/Vite frontend
-   Groq-powered LLM integration
-   Swagger API documentation
-   Production deployment with Vercel and Render

## Interview Completion

The backend tracks both the number of questions and curriculum coverage.

``` text
question_count >= 8
AND
covered_days >= 4
```

The final response contains:

``` json
{
  "reply": "Thank you. That concludes the technical interview.",
  "done": true,
  "feedback": {
    "summary": "...",
    "strengths": [],
    "gaps": [],
    "next": []
  }
}
```

## API

### `POST /api/interview`

The API does not require authentication.

### Start an Interview

``` json
{
  "sessionId": "abc-123",
  "candidate": {
    "member": {
      "id": "CAND-001"
    }
  }
}
```

Example response:

``` json
{
  "reply": "Can you explain ...?",
  "done": false,
  "feedback": null
}
```

### Continue an Interview

Use the same `sessionId`:

``` json
{
  "sessionId": "abc-123",
  "message": "Candidate's answer..."
}
```

Example response:

``` json
{
  "reply": "How would you ...?",
  "done": false,
  "feedback": null
}
```

### Complete an Interview

After the interview requirements are satisfied:

``` json
{
  "reply": "Thank you. That concludes the technical interview.",
  "done": true,
  "feedback": {
    "summary": "Candidate evaluation...",
    "strengths": [
      "Strength demonstrated during the interview."
    ],
    "gaps": [
      "Area that needs improvement."
    ],
    "next": [
      "Recommended next learning step."
    ]
  }
}
```

## Feedback Format

  -----------------------------------------------------------------------
  Field                   Type                    Description
  ----------------------- ----------------------- -----------------------
  `summary`               string                  Overall interview
                                                  evaluation

  `strengths`             string\[\]              Candidate strengths
                                                  demonstrated during the
                                                  interview

  `gaps`                  string\[\]              Areas where the
                                                  candidate needs
                                                  improvement

  `next`                  string\[\]              Actionable next
                                                  learning steps
  -----------------------------------------------------------------------

## Technology Stack

### Frontend

-   React
-   Vite
-   JavaScript
-   CSS

### Backend

-   Python
-   FastAPI
-   Pydantic
-   Uvicorn
-   Python dotenv

### AI

-   Groq API
-   LLM-based interview planning and question generation
-   Context-aware follow-up generation
-   LLM-generated final feedback

### Deployment

-   Vercel --- frontend
-   Render --- backend
-   GitHub --- source repository

## Local Development

### Backend

``` powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a local `.env` file:

``` env
GROQ_API_KEY=your_groq_api_key
```

Start FastAPI:

``` powershell
uvicorn app.main:app --reload
```

Backend:

``` text
http://127.0.0.1:8000
```

Swagger:

``` text
http://127.0.0.1:8000/docs
```

### Frontend

``` powershell
cd frontend
npm install
npm run dev
```

For local development:

``` env
VITE_API_URL=http://127.0.0.1:8000
```

For production, the frontend communicates with the deployed Render
backend.

## Production Architecture

``` text
                    ┌─────────────────────┐
                    │       Judge/User     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Vercel Frontend   │
                    │     React + Vite    │
                    └──────────┬──────────┘
                               │
                         HTTP POST
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Render Backend     │
                    │ FastAPI + Uvicorn   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Interview Logic   │
                    │ Session + Context   │
                    │ Planner + Feedback  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Groq LLM       │
                    └─────────────────────┘
```

## Testing

The project was verified through:

-   Local backend execution
-   Backend end-to-end interview testing
-   Production Render API
-   Production Vercel frontend
-   FastAPI Swagger `/docs`
-   Sequential multi-turn API requests using the same `sessionId`
-   8-question completion flow
-   Final structured feedback generation

The deployed API was manually tested through Swagger using the
production endpoint.

## Security

API secrets are kept in environment variables and are not committed to
the public repository.

The Groq API key is configured in the deployment environment rather than
exposed in the frontend.

## Deployment

### Backend

The backend is deployed on Render with:

``` text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend

The frontend is deployed on Vercel and communicates with the Render
backend through the production API URL.

## Project Goal

The goal of the project is to demonstrate a practical AI-powered
technical interviewer that maintains conversational state, adapts
questions based on candidate responses and learning context, and
produces useful, structured feedback at the end of the interview.
