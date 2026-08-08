import json

from app.models.interview_profile import InterviewProfile
from app.models.interview_plan import InterviewPlan


class InterviewContextBuilder:

    def build(
        self,
        profile: InterviewProfile,
        plan: InterviewPlan,
        curriculum_day: dict | None,
        conversation: list[dict],
        question_number: int,
        covered_days: list[int],
        latest_answer: str | None = None,
    ) -> str:

        candidate_context = {
            "candidate_id": profile.candidate_id,
            "candidate_name": profile.candidate_name,
            "job_role": profile.job_role,
            "years_experience": profile.years_experience,
            "education": profile.education,
            "missions_completed": profile.missions_completed,
            "missions_first_try": profile.missions_first_try,
            "commit_days": profile.commit_days,
        }

        learning_signals = {
            "strengths": [
                {
                    "day": topic.day,
                    "title": topic.title,
                    "status": topic.status,
                    "attempts": topic.attempts,
                    "reason": topic.reason,
                }
                for topic in profile.strengths
            ],
            "developing_areas": [
                {
                    "day": topic.day,
                    "title": topic.title,
                    "status": topic.status,
                    "attempts": topic.attempts,
                    "reason": topic.reason,
                }
                for topic in profile.weak_areas
            ],
            "skipped_topics": [
                {
                    "day": topic.day,
                    "title": topic.title,
                    "status": topic.status,
                    "attempts": topic.attempts,
                    "reason": topic.reason,
                }
                for topic in profile.skipped_topics
            ],
        }

        plan_context = {
            "minimum_questions": plan.minimum_questions,
            "minimum_curriculum_days": plan.minimum_curriculum_days,
            "planned_questions": plan.planned_questions,
            "planned_curriculum_days": plan.planned_curriculum_days,
            "phases": [
                {
                    "name": phase.name,
                    "purpose": phase.purpose,
                    "topics": [
                        {
                            "day": topic.day,
                            "title": topic.title,
                            "phase": topic.phase,
                            "priority": topic.priority,
                            "difficulty": topic.difficulty,
                            "reason": topic.reason,
                        }
                        for topic in phase.topics
                    ],
                }
                for phase in plan.phases
            ],
        }

        curriculum_context = None

        if curriculum_day:
            curriculum_context = {
                "day": curriculum_day.get("day"),
                "title": curriculum_day.get("title"),
                "type": curriculum_day.get("type"),
                "tools": curriculum_day.get("tools", []),
                "objectives": curriculum_day.get("objectives", []),
            }

        context = {
            "interview_state": {
                "question_number": question_number,
                "minimum_questions": 8,
                "minimum_curriculum_days": 4,
                "covered_curriculum_days": covered_days,
            },
            "candidate": candidate_context,
            "learning_signals": learning_signals,
            "interview_plan": plan_context,
            "current_curriculum_topic": curriculum_context,
            "conversation": conversation,
            "latest_candidate_answer": latest_answer,
        }

        return json.dumps(
            context,
            indent=2,
            ensure_ascii=False,
        )