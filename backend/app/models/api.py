from pydantic import BaseModel


class InterviewRequest(BaseModel):
    sessionId: str
    candidate: dict | None = None
    message: str | None = None


class Feedback(BaseModel):
    summary: str
    strengths: list[str]
    gaps: list[str]
    next: list[str]


class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Feedback | None = None