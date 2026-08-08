from pydantic import BaseModel
from typing import Optional


class Mission(BaseModel):
    day: int
    title: str
    passed: Optional[bool] = None
    skipped: Optional[bool] = None
    attempts: Optional[int] = None


class LearningSignals(BaseModel):
    commitDays: int
    missionsCompleted: int
    missionsFirstTry: int


class CandidateMember(BaseModel):
    id: str
    name: str
    jobRole: str
    yearsExperience: int
    education: str
    status: str


class Candidate(BaseModel):
    member: CandidateMember
    missions: list[Mission]
    signals: LearningSignals