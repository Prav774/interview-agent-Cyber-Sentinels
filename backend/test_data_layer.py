from app.services.candidate_service import CandidateService
from app.services.curriculum_service import CurriculumService


candidate_service = CandidateService()
curriculum_service = CurriculumService()


candidate = candidate_service.get_candidate("CAND-002")

print("Candidate:")
print(candidate.member.name)
print(candidate.member.jobRole)

print("\nMissions:")
for mission in candidate.missions:
    print(mission.day, "-", mission.title)

day_12 = curriculum_service.get_day(12)

print("\nCurriculum Day 12:")
print(day_12["title"])
print(day_12["objectives"])