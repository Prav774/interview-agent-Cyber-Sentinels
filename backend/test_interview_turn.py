from app.services.candidate_service import CandidateService
from app.services.curriculum_service import CurriculumService
from app.services.candidate_analyzer import CandidateAnalyzer
from app.services.interview_planner import InterviewPlanner
from app.services.context_builder import InterviewContextBuilder
from app.services.llm_service import LLMService
from app.prompts.interviewer import INTERVIEWER_SYSTEM_PROMPT


candidate_service = CandidateService()
curriculum_service = CurriculumService()
analyzer = CandidateAnalyzer()
planner = InterviewPlanner()
context_builder = InterviewContextBuilder()
llm = LLMService()


candidate = candidate_service.get_candidate("CAND-001")

profile = analyzer.analyze(candidate)
plan = planner.create_plan(profile)

current_topic = curriculum_service.get_day(12)

conversation = [
    {
        "role": "assistant",
        "content": (
            "You passed your prompt engineering mission. "
            "How would you design a production system prompt "
            "for an AI application?"
        ),
    },
    {
        "role": "user",
        "content": (
            "I would start with a system prompt and then "
            "test different variations."
        ),
    },
]

context = context_builder.build(
    profile=profile,
    plan=plan,
    curriculum_day=current_topic,
    conversation=conversation,
    question_number=2,
    covered_days=[7, 12],
    latest_answer=(
        "I would start with a system prompt and then "
        "test different variations."
    ),
)

result = llm.generate_interview_turn(
    system_prompt=INTERVIEWER_SYSTEM_PROMPT,
    context=context,
)

print("\n" + "=" * 70)
print("LLM INTERVIEW TURN")
print("=" * 70)

print("\nEvaluation:")
print(result.evaluation)

print("\nAnswer quality:")
print(result.answer_quality)

print("\nNext action:")
print(result.next_action)

print("\nNext question:")
print(result.next_question)

print("\nTopic day:")
print(result.topic_day)

print("\nTopic:")
print(result.topic)