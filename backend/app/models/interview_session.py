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

    # Current topic being assessed.
    # Follow-up questions stay on this topic.
    current_topic_index: int = 0
    current_topic_day: int | None = None
    current_topic_title: str | None = None

    follow_ups_on_current_topic: int = 0

    done: bool = False