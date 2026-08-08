from pydantic import BaseModel
from typing import Optional


class InterviewLLMResponse(BaseModel):
    evaluation: Optional[str] = None
    answer_quality: Optional[str] = None
    next_action: str
    next_question: str
    topic_day: Optional[int] = None
    topic: Optional[str] = None


class InterviewFeedback(BaseModel):
    summary: str
    strengths: list[str]
    gaps: list[str]
    next: list[str]