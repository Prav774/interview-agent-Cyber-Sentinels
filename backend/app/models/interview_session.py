from pydantic import BaseModel, Field


class InterviewMessage(BaseModel):
    role: str
    content: str


class InterviewSession(BaseModel):
    session_id: str
    candidate_id: str
    candidate_name: str

    profile: object
    plan: object

    conversation: list[InterviewMessage] = Field(default_factory=list)

    question_count: int = 0
    covered_days: list[int] = Field(default_factory=list)

    done: bool = False