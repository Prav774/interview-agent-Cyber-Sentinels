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

        # =====================================================
        # CANDIDATE
        # =====================================================

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

        # =====================================================
        # CURRENT TOPIC LEARNING SIGNAL
        # =====================================================

        current_day = None

        if curriculum_day:
            current_day = curriculum_day.get("day")

        current_signal = None

        if current_day is not None:

            all_signals = (
                list(profile.strengths)
                + list(profile.weak_areas)
                + list(profile.skipped_topics)
            )

            for topic in all_signals:

                if topic.day == current_day:

                    current_signal = {
                        "day": topic.day,
                        "title": topic.title,
                        "status": topic.status,
                        "attempts": topic.attempts,
                        "reason": topic.reason,
                    }

                    break

        # =====================================================
        # CURRENT CURRICULUM
        # =====================================================

        curriculum_context = None

        if curriculum_day:

            curriculum_context = {
                "day": curriculum_day.get("day"),
                "title": curriculum_day.get("title"),
                "type": curriculum_day.get("type"),
                "tools": curriculum_day.get("tools", []),
                "objectives": curriculum_day.get(
                    "objectives",
                    [],
                ),
            }

        # =====================================================
        # INTERVIEW STATE
        # =====================================================

        interview_state = {
            "question_number": question_number,
            "minimum_questions": plan.minimum_questions,
            "minimum_curriculum_days": (
                plan.minimum_curriculum_days
            ),
            "covered_curriculum_days": covered_days,
        }

        # =====================================================
        # RECENT CONVERSATION
        # =====================================================

        # Keep enough conversation for natural follow-ups
        # without repeatedly sending a huge transcript.
        #
        # At the end of the interview, the complete session is
        # still stored by SessionManager.

        max_recent_messages = 8

        recent_conversation = conversation[
            -max_recent_messages:
        ]

        # =====================================================
        # COMPACT CONTEXT
        # =====================================================

        context = {
            "interview_state": interview_state,

            "candidate": candidate_context,

            "current_learning_signal": current_signal,

            "current_curriculum_topic": curriculum_context,

            "conversation": recent_conversation,

            "latest_candidate_answer": latest_answer,
        }

        return json.dumps(
            context,
            indent=2,
            ensure_ascii=False,
        )