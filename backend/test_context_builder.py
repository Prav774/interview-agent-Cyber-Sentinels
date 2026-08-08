from app.services.candidate_service import CandidateService
from app.services.curriculum_service import CurriculumService
from app.services.candidate_analyzer import CandidateAnalyzer
from app.services.interview_planner import InterviewPlanner
from app.services.context_builder import InterviewContextBuilder


candidate_service = CandidateService()
curriculum_service = CurriculumService()
analyzer = CandidateAnalyzer()
planner = InterviewPlanner()
builder = InterviewContextBuilder()


candidate = candidate_service.get_candidate("CAND-001")

profile = analyzer.analyze(candidate)
plan = planner.create_plan(profile)

current_topic = curriculum_service.get_day(12)

context = builder.build(
    profile=profile,
    plan=plan,
    curriculum_day=current_topic,
    conversation=[
        {
            "role": "assistant",
            "content": "How would you design a production prompt?"
        },
        {
            "role": "user",
            "content": (
                "I would start with a system prompt and "
                "then test different variations."
            ),
        },
    ],
    question_number=2,
    covered_days=[7, 12],
    latest_answer=(
        "I would start with a system prompt and "
        "then test different variations."
    ),
)

print(context)