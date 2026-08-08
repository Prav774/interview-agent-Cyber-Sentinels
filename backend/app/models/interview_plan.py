from pydantic import BaseModel


class PlannedTopic(BaseModel):
    day: int
    title: str
    phase: str
    priority: str
    difficulty: str
    reason: str


class InterviewPhase(BaseModel):
    name: str
    purpose: str
    topics: list[PlannedTopic]


class InterviewPlan(BaseModel):
    candidate_id: str
    candidate_name: str
    phases: list[InterviewPhase]

    minimum_questions: int = 8
    minimum_curriculum_days: int = 4

    planned_questions: int
    planned_curriculum_days: int