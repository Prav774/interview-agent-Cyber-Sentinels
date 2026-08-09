from app.services.llm_service import LLMService

llm = LLMService()

result = llm.generate_interview_turn(
    system_prompt=(
        "You are a technical interviewer. "
        "Ask one concise technical interview question "
        "about AI engineering."
    ),
    context={
        "current_curriculum_topic": {
            "day": 7,
            "title": "Embeddings Explained",
            "objectives": [
                "Understand text embeddings",
                "Understand semantic similarity",
                "Understand vector representations",
            ],
        },
        "candidate": {
            "candidate_name": "Sarah Johnson",
            "job_role": "Senior Data Engineer",
        },
        "conversation": [],
        "latest_candidate_answer": None,
        "interview_state": {
            "question_number": 1,
            "minimum_questions": 8,
            "minimum_curriculum_days": 4,
            "covered_curriculum_days": [],
        },
    },
)

print("\nLLM RESPONSE:\n")
print("Question:", result.next_question)
print("Action:", result.next_action)
print("Quality:", result.answer_quality)