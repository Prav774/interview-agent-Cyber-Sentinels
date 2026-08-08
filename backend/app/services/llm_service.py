import json
import os

from dotenv import load_dotenv
from groq import Groq

from app.models.llm_response import InterviewLLMResponse


load_dotenv()


class LLMService:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    def generate_interview_turn(
        self,
        system_prompt: str,
        context: str,
    ) -> InterviewLLMResponse:

        user_prompt = f"""
Here is the current interview context.

Return ONLY valid JSON.
Do not use markdown.
Do not include ```json fences.

Required JSON structure:

{{
  "evaluation": "brief evaluation of the candidate's latest answer",
  "answer_quality": "strong | adequate | weak | unclear",
  "next_action": "ask | follow_up | complete",
  "next_question": "exactly one question for the candidate",
  "topic_day": 0,
  "topic": "curriculum topic"
}}

Rules:

- Ask exactly one question.
- Do not expose your internal reasoning.
- Keep the question grounded in the supplied curriculum.
- If the latest answer needs deeper probing, use "follow_up".
- Otherwise use "ask".
- Use "complete" only when the application state allows the
  interview to finish.
- topic_day must refer to a curriculum day present in the context.

CURRENT CONTEXT:

{context}
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content

        try:
            data = json.loads(raw_content)
            return InterviewLLMResponse(**data)

        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeError(
                f"Invalid structured response from LLM: {raw_content}"
            ) from exc