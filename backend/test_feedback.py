from app.services.llm_service import LLMService
from app.prompts.interviewer import INTERVIEWER_SYSTEM_PROMPT


llm = LLMService()

context = """
Candidate: Sarah Johnson
Role: Senior Data Engineer

Interview topics covered:
Day 7 - Embeddings Explained
Day 10 - Retrieval & Matching Engine
Day 12 - Prompt Engineering Fundamentals
Day 29 - Monitoring, Logging & Observability

Interview observations:

1. Candidate correctly explained that embeddings represent
   semantic relationships using vectors.

2. Candidate initially gave a shallow answer and required
   a follow-up.

3. Candidate demonstrated understanding of vector similarity
   and retrieval.

4. Candidate could explain prompt experimentation but did not
   initially discuss systematic evaluation.

5. Candidate struggled to explain monitoring and observability
   concepts in depth.

Conversation:
Interviewer: Explain how embeddings represent semantic meaning.
Candidate: Embeddings turn text into numbers.

Interviewer: Can you elaborate on how embeddings achieve this?
Candidate: Embeddings represent semantic relationships by mapping
similar meanings to nearby vectors.

Interviewer: How would you evaluate different prompt variations?
Candidate: I would test different prompts against examples and
compare the results.

Interviewer: How would you monitor a production RAG system?
Candidate: I would monitor whether the system is working and check
the logs.
"""


feedback = llm.generate_feedback(
    system_prompt=INTERVIEWER_SYSTEM_PROMPT,
    context=context,
)

print("\n" + "=" * 70)
print("FINAL INTERVIEW FEEDBACK")
print("=" * 70)

print("\nSUMMARY:")
print(feedback.summary)

print("\nSTRENGTHS:")
for item in feedback.strengths:
    print(f"- {item}")

print("\nGAPS:")
for item in feedback.gaps:
    print(f"- {item}")

print("\nNEXT STEPS:")
for item in feedback.next:
    print(f"- {item}")