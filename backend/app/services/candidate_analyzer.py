from app.models.candidate import Candidate
from app.models.interview_profile import (
    InterviewProfile,
    TopicAnalysis,
)


class CandidateAnalyzer:

    def analyze(self, candidate: Candidate) -> InterviewProfile:

        strengths = []
        weak_areas = []
        skipped_topics = []

        for mission in candidate.missions:

            attempts = mission.attempts or 0

            # Explicitly skipped topic
            if mission.skipped:
                skipped_topics.append(
                    TopicAnalysis(
                        day=mission.day,
                        title=mission.title,
                        status="skipped",
                        attempts=attempts,
                        reason="Candidate skipped this topic.",
                    )
                )
                continue

            # Explicitly failed topic
            if mission.passed is False:
                weak_areas.append(
                    TopicAnalysis(
                        day=mission.day,
                        title=mission.title,
                        status="failed",
                        attempts=attempts,
                        reason="Mission was not passed.",
                    )
                )
                continue

            # Passed on first attempt
            if mission.passed and attempts == 1:
                strengths.append(
                    TopicAnalysis(
                        day=mission.day,
                        title=mission.title,
                        status="strong",
                        attempts=attempts,
                        reason="Mission passed on the first attempt.",
                    )
                )
                continue

            # Passed but required multiple attempts
            if mission.passed and attempts > 1:
                weak_areas.append(
                    TopicAnalysis(
                        day=mission.day,
                        title=mission.title,
                        status="developing",
                        attempts=attempts,
                        reason=f"Mission passed after {attempts} attempts.",
                    )
                )

        return InterviewProfile(
            candidate_id=candidate.member.id,
            candidate_name=candidate.member.name,
            job_role=candidate.member.jobRole,
            years_experience=candidate.member.yearsExperience,
            education=candidate.member.education,
            strengths=strengths,
            weak_areas=weak_areas,
            skipped_topics=skipped_topics,
            missions_completed=candidate.signals.missionsCompleted,
            missions_first_try=candidate.signals.missionsFirstTry,
            commit_days=candidate.signals.commitDays,
        )