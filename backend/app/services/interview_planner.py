from app.models.interview_profile import InterviewProfile
from app.models.interview_plan import (
    InterviewPlan,
    InterviewPhase,
    PlannedTopic,
)


class InterviewPlanner:

    def create_plan(
        self,
        profile: InterviewProfile,
    ) -> InterviewPlan:

        # ---------------------------------------------------------
        # Categorize candidate topics
        # ---------------------------------------------------------

        failed = [
            topic
            for topic in profile.weak_areas
            if topic.status == "failed"
        ]

        developing = [
            topic
            for topic in profile.weak_areas
            if topic.status == "developing"
        ]

        skipped = profile.skipped_topics
        strengths = profile.strengths

        # ---------------------------------------------------------
        # Phase 1: Warm-up
        #
        # Use a demonstrated strength to establish baseline.
        # ---------------------------------------------------------

        warmup_topics = []

        if strengths:
            topic = strengths[0]

            warmup_topics.append(
                PlannedTopic(
                    day=topic.day,
                    title=topic.title,
                    phase="warmup",
                    priority="MEDIUM",
                    difficulty="MEDIUM",
                    reason=(
                        "Candidate demonstrated first-attempt "
                        "success in this topic."
                    ),
                )
            )

        # ---------------------------------------------------------
        # Phase 2: Core Assessment
        #
        # Developing topics are useful for assessing actual depth.
        # ---------------------------------------------------------

        core_topics = []

        for topic in developing[:2]:

            difficulty = (
                "HARD"
                if topic.attempts >= 4
                else "MEDIUM"
            )

            core_topics.append(
                PlannedTopic(
                    day=topic.day,
                    title=topic.title,
                    phase="core_assessment",
                    priority="HIGH",
                    difficulty=difficulty,
                    reason=(
                        f"Candidate passed after "
                        f"{topic.attempts} attempts."
                    ),
                )
            )

        # ---------------------------------------------------------
        # Phase 3: Candidate-specific probing
        #
        # Failed and skipped topics are strong diagnostic signals.
        # ---------------------------------------------------------

        diagnostic_topics = []

        for topic in failed:

            diagnostic_topics.append(
                PlannedTopic(
                    day=topic.day,
                    title=topic.title,
                    phase="candidate_specific_probe",
                    priority="HIGH",
                    difficulty="MEDIUM",
                    reason="Candidate did not pass this mission.",
                )
            )

        for topic in skipped:

            diagnostic_topics.append(
                PlannedTopic(
                    day=topic.day,
                    title=topic.title,
                    phase="candidate_specific_probe",
                    priority="HIGH",
                    difficulty="MEDIUM",
                    reason="Candidate skipped this curriculum topic.",
                )
            )

        # ---------------------------------------------------------
        # Phase 4: Deep Technical Assessment
        #
        # Strong topics are tested at a higher conceptual level.
        # ---------------------------------------------------------

        deep_topics = []

        for topic in strengths[1:]:

            deep_topics.append(
                PlannedTopic(
                    day=topic.day,
                    title=topic.title,
                    phase="deep_technical_assessment",
                    priority="MEDIUM",
                    difficulty="HARD",
                    reason=(
                        "Candidate demonstrated first-attempt "
                        "success; test depth rather than recall."
                    ),
                )
            )

        # ---------------------------------------------------------
        # Combine candidate topics while avoiding duplicate days.
        # ---------------------------------------------------------

        phases = [
            InterviewPhase(
                name="warmup",
                purpose="Establish the candidate's technical baseline.",
                topics=warmup_topics,
            ),
            InterviewPhase(
                name="core_assessment",
                purpose="Assess understanding of developing areas.",
                topics=core_topics,
            ),
            InterviewPhase(
                name="candidate_specific_probe",
                purpose=(
                    "Investigate failed, skipped, or uncertain "
                    "areas from the candidate journey."
                ),
                topics=diagnostic_topics,
            ),
            InterviewPhase(
                name="deep_technical_assessment",
                purpose=(
                    "Test whether demonstrated strengths represent "
                    "real technical depth."
                ),
                topics=deep_topics,
            ),
        ]

        # ---------------------------------------------------------
        # Select primary questions.
        #
        # Requirements:
        #   - minimum 8 questions
        #   - minimum 4 curriculum days
        #
        # We only use topics actually present in the candidate's
        # supplied journey.
        # ---------------------------------------------------------

        selected: list[PlannedTopic] = []
        selected_days: set[int] = set()

        # First guarantee curriculum-day diversity.
        all_topics = [
            topic
            for phase in phases
            for topic in phase.topics
        ]

        for topic in all_topics:

            if topic.day in selected_days:
                continue

            if len(selected_days) < 4:
                selected.append(topic)
                selected_days.add(topic.day)

        # Then fill remaining primary-question slots.
        for topic in all_topics:

            if len(selected) >= 8:
                break

            if topic.day in selected_days:
                continue

            selected.append(topic)
            selected_days.add(topic.day)

        # ---------------------------------------------------------
        # If fewer than 8 unique candidate topics exist,
        # use additional topics from the curriculum journey,
        # allowing the same curriculum day to receive another
        # question later through adaptive follow-up generation.
        #
        # We do NOT invent topics outside the candidate profile.
        # ---------------------------------------------------------

        if len(selected) < 8:

            for topic in all_topics:

                if len(selected) >= 8:
                    break

                selected.append(topic)

        # ---------------------------------------------------------
        # Rebuild phases using only selected primary topics.
        # ---------------------------------------------------------

        selected_ids = {
            (topic.day, topic.title, topic.phase)
            for topic in selected
        }

        final_phases = []

        for phase in phases:

            phase_topics = [
                topic
                for topic in phase.topics
                if (topic.day, topic.title, topic.phase)
                in selected_ids
            ]

            if phase_topics:
                final_phases.append(
                    InterviewPhase(
                        name=phase.name,
                        purpose=phase.purpose,
                        topics=phase_topics,
                    )
                )

        return InterviewPlan(
            candidate_id=profile.candidate_id,
            candidate_name=profile.candidate_name,
            phases=final_phases,
            minimum_questions=8,
            minimum_curriculum_days=4,
            planned_questions=len(selected),
            planned_curriculum_days=len(selected_days),
        )