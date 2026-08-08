from app.models.interview_session import InterviewSession


class SessionManager:

    def __init__(self):
        self.sessions: dict[str, InterviewSession] = {}

    def create_session(
        self,
        session_id: str,
        candidate_id: str,
        candidate_name: str,
        profile,
        plan,
    ) -> InterviewSession:

        session = InterviewSession(
            session_id=session_id,
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            profile=profile,
            plan=plan,
        )

        self.sessions[session_id] = session

        return session

    def get_session(
        self,
        session_id: str,
    ) -> InterviewSession | None:

        return self.sessions.get(session_id)

    def save_session(
        self,
        session: InterviewSession,
    ) -> None:

        self.sessions[session.session_id] = session