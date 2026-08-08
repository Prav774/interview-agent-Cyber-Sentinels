from pydantic import BaseModel


class TopicAnalysis(BaseModel):
    day: int
    title: str
    status: str
    attempts: int = 0
    reason: str


class InterviewProfile(BaseModel):
    candidate_id: str
    candidate_name: str
    job_role: str
    years_experience: int
    education: str

    strengths: list[TopicAnalysis]
    weak_areas: list[TopicAnalysis]
    skipped_topics: list[TopicAnalysis]

    missions_completed: int
    missions_first_try: int
    commit_days: int