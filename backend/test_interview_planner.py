from app.services.candidate_service import CandidateService
from app.services.candidate_analyzer import CandidateAnalyzer
from app.services.interview_planner import InterviewPlanner


candidate_service = CandidateService()
analyzer = CandidateAnalyzer()
planner = InterviewPlanner()


def test_candidate(candidate_id: str):

    candidate = candidate_service.get_candidate(candidate_id)

    if candidate is None:
        print(f"Candidate {candidate_id} not found.")
        return

    profile = analyzer.analyze(candidate)
    plan = planner.create_plan(profile)

    print("\n" + "=" * 70)
    print(
        f"INTERVIEW STRATEGY — "
        f"{plan.candidate_name}"
    )
    print("=" * 70)

    print(f"Candidate ID: {plan.candidate_id}")
    print(f"Minimum questions: {plan.minimum_questions}")
    print(
        f"Minimum curriculum days: "
        f"{plan.minimum_curriculum_days}"
    )
    print(
        f"Planned questions: "
        f"{plan.planned_questions}"
    )
    print(
        f"Planned curriculum days: "
        f"{plan.planned_curriculum_days}"
    )

    print("\nPHASES")

    for phase in plan.phases:

        print("\n" + "-" * 60)
        print(f"{phase.name.upper()}")
        print(f"Purpose: {phase.purpose}")

        for topic in phase.topics:

            print(
                f"\nDay {topic.day}: {topic.title}"
            )
            print(
                f"  Priority: {topic.priority}"
            )
            print(
                f"  Difficulty: {topic.difficulty}"
            )
            print(
                f"  Reason: {topic.reason}"
            )


test_candidate("CAND-001")
test_candidate("CAND-003")
test_candidate("CAND-010")
test_candidate("CAND-011")