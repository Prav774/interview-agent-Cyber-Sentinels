from fastapi import FastAPI

from app.api.interview import router as interview_router


app = FastAPI(
    title="AI Interview Agent",
    description="Adaptive technical interview agent for VibeCodathon",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "AI Interview Agent API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


app.include_router(
    interview_router,
    prefix="/api",
)