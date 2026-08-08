from fastapi import APIRouter, HTTPException

from app.models.api import (
    InterviewRequest,
    InterviewResponse,
)

from app.services.candidate_service import CandidateService
from app.services.candidate_analyzer import CandidateAnalyzer
from app.services.interview_planner import InterviewPlanner
from app.services.curriculum_service import CurriculumService
from app.services.context_builder import InterviewContextBuilder
from app.services.llm_service import LLMService

from app.core.session_manager import SessionManager

from app.prompts.interviewer import INTERVIEWER_SYSTEM_PROMPT


router = APIRouter()

candidate_service = CandidateService()
candidate_analyzer = CandidateAnalyzer()
interview_planner = InterviewPlanner()
curriculum_service = CurriculumService()
context_builder = InterviewContextBuilder()
llm_service = LLMService()
session_manager = SessionManager()


@router.post(
    "/interview",
    response_model=InterviewResponse,
)
def interview(
    request: InterviewRequest,
):

    # ---------------------------------------------------------
    # FIRST REQUEST
    # ---------------------------------------------------------

    session = session_manager.get_session(
        request.sessionId
    )

    if session is None:

        if not request.candidate:
            raise HTTPException(
                status_code=400,
                detail="Candidate data is required for the first request.",
            )

        candidate_id = request.candidate["member"]["id"]

        candidate = candidate_service.get_candidate(
            candidate_id
        )

        if candidate is None:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found.",
            )

        profile = candidate_analyzer.analyze(candidate)

        plan = interview_planner.create_plan(profile)

        session = session_manager.create_session(
            session_id=request.sessionId,
            candidate_id=candidate.member.id,
            candidate_name=candidate.member.name,
            profile=profile,
            plan=plan,
        )

    # ---------------------------------------------------------
    # CANDIDATE MESSAGE
    # ---------------------------------------------------------

    if request.message:

        session.conversation.append(
            {
                "role": "user",
                "content": request.message,
            }
        )

    # ---------------------------------------------------------
    # DETERMINE CURRENT TOPIC
    # ---------------------------------------------------------

    if session.plan.phases:

        all_topics = [
            topic
            for phase in session.plan.phases
            for topic in phase.topics
        ]

        if all_topics:

            index = min(
                session.question_count,
                len(all_topics) - 1,
            )

            current_topic = all_topics[index]

            curriculum_day = (
                curriculum_service.get_day(
                    current_topic.day
                )
            )

        else:
            curriculum_day = None

    else:
        curriculum_day = None

    # ---------------------------------------------------------
    # BUILD LLM CONTEXT
    # ---------------------------------------------------------

    conversation = [
        {
            "role": message["role"]
            if isinstance(message, dict)
            else message.role,
            "content": message["content"]
            if isinstance(message, dict)
            else message.content,
        }
        for message in session.conversation
    ]

    latest_answer = (
        request.message
        if request.message
        else None
    )

    context = context_builder.build(
        profile=session.profile,
        plan=session.plan,
        curriculum_day=curriculum_day,
        conversation=conversation,
        question_number=session.question_count + 1,
        covered_days=session.covered_days,
        latest_answer=latest_answer,
    )

    # ---------------------------------------------------------
    # ASK GROQ
    # ---------------------------------------------------------

    result = llm_service.generate_interview_turn(
        system_prompt=INTERVIEWER_SYSTEM_PROMPT,
        context=context,
    )

    # ---------------------------------------------------------
    # TRACK QUESTION / CURRICULUM COVERAGE
    # ---------------------------------------------------------

    if result.topic_day is not None:

        if result.topic_day not in session.covered_days:
            session.covered_days.append(
                result.topic_day
            )

    session.conversation.append(
        {
            "role": "assistant",
            "content": result.next_question,
        }
    )

    session.question_count += 1

    # ---------------------------------------------------------
    # TEMPORARY COMPLETION GUARD
    # ---------------------------------------------------------

    if (
        session.question_count >= 8
        and len(session.covered_days) >= 4
        and result.next_action == "complete"
    ):
        session.done = True

    session_manager.save_session(session)

    return InterviewResponse(
        reply=result.next_question,
        done=session.done,
        feedback=None,
    )