from app.services.candidate_service import CandidateService
from app.services.candidate_analyzer import CandidateAnalyzer


candidate_service = CandidateService()
analyzer = CandidateAnalyzer()


def print_profile(candidate_id: str):

    candidate = candidate_service.get_candidate(candidate_id)

    if candidate is None:
        print(f"Candidate {candidate_id} not found.")
        return

    profile = analyzer.analyze(candidate)

    print("\n" + "=" * 60)
    print(f"{profile.candidate_name} — {profile.job_role}")
    print("=" * 60)

    print(f"Experience: {profile.years_experience} years")
    print(f"Completed: {profile.missions_completed}")
    print(f"First try: {profile.missions_first_try}")
    print(f"Commit days: {profile.commit_days}")

    print("\nSTRENGTHS")
    for topic in profile.strengths:
        print(f"  Day {topic.day}: {topic.title}")

    print("\nDEVELOPING / WEAK AREAS")
    for topic in profile.weak_areas:
        print(
            f"  Day {topic.day}: {topic.title} "
            f"({topic.attempts} attempts)"
        )

    print("\nSKIPPED")
    for topic in profile.skipped_topics:
        print(f"  Day {topic.day}: {topic.title}")


print_profile("CAND-001")
print_profile("CAND-003")
print_profile("CAND-010")