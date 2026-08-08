from app.services.llm_service import LLMService


llm = LLMService()

response = llm.generate(
    system_prompt=(
        "You are a technical interviewer. "
        "Ask one concise technical question."
    ),
    user_prompt=(
        "Ask a question about vector databases "
        "for an AI engineer."
    ),
)

print("\nLLM RESPONSE:\n")
print(response)