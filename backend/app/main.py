from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.interview import router as interview_router


app = FastAPI(
    title="AI Interview Agent",
    description="Adaptive technical interview agent for VibeCodathon",
    version="0.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Interview Agent API is running",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# INTERVIEW API
# ============================================================

app.include_router(
    interview_router,
    prefix="/api",
)