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


def get_all_planned_topics(plan):
    """Flatten all interview phases into one ordered topic list."""

    return [
        topic
        for phase in plan.phases
        for topic in phase.topics
    ]


def get_current_topic(session):
    """Return the curriculum topic currently being assessed."""

    topics = get_all_planned_topics(session.plan)

    if not topics:
        return None

    index = min(
        session.current_topic_index,
        len(topics) - 1,
    )

    return topics[index]


def move_to_next_topic(session):
    """Advance to the next planned curriculum topic."""

    topics = get_all_planned_topics(session.plan)

    if not topics:
        return None

    if session.current_topic_index < len(topics) - 1:
        session.current_topic_index += 1

    return get_current_topic(session)


@router.post(
    "/interview",
    response_model=InterviewResponse,
)
def interview(
    request: InterviewRequest,
):

    # =========================================================
    # CREATE / RESTORE SESSION
    # =========================================================

    session = session_manager.get_session(
        request.sessionId
    )

    if session is None:

        if not request.candidate:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Candidate data is required "
                    "for the first request."
                ),
            )

        try:
            candidate_id = request.candidate["member"]["id"]
        except (KeyError, TypeError):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Candidate must contain "
                    "member.id."
                ),
            )

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

    # =========================================================
    # ADD CANDIDATE ANSWER TO CONVERSATION
    # =========================================================

    if request.message:

        session.conversation.append(
            {
                "role": "user",
                "content": request.message,
            }
        )

    # =========================================================
    # INITIAL QUESTION
    # =========================================================

    if session.question_count == 0:

        current_topic = get_current_topic(session)

        if current_topic is None:
            raise HTTPException(
                status_code=500,
                detail="Interview plan contains no topics.",
            )

        session.current_topic_day = current_topic.day
        session.current_topic_title = current_topic.title

    # =========================================================
    # BUILD CURRICULUM CONTEXT
    # =========================================================

    current_topic = get_current_topic(session)

    if current_topic is None:
        raise HTTPException(
            status_code=500,
            detail="Unable to determine current interview topic.",
        )

    curriculum_day = curriculum_service.get_day(
        current_topic.day
    )

    # =========================================================
    # BUILD CONVERSATION FOR LLM
    # =========================================================

    conversation = [
        {
            "role": (
                message["role"]
                if isinstance(message, dict)
                else message.role
            ),
            "content": (
                message["content"]
                if isinstance(message, dict)
                else message.content
            ),
        }
        for message in session.conversation
    ]

    latest_answer = (
        request.message
        if request.message
        else None
    )

    # =========================================================
    # BUILD LLM CONTEXT
    # =========================================================

    context = context_builder.build(
        profile=session.profile,
        plan=session.plan,
        curriculum_day=curriculum_day,
        conversation=conversation,
        question_number=session.question_count + 1,
        covered_days=session.covered_days,
        latest_answer=latest_answer,
    )

    # =========================================================
    # ASK GROQ
    # =========================================================

    result = llm_service.generate_interview_turn(
        system_prompt=INTERVIEWER_SYSTEM_PROMPT,
        context=context,
    )

    # =========================================================
    # ADAPTIVE TOPIC CONTROL
    # =========================================================

    is_follow_up = (
        session.question_count > 0
        and result.next_action == "follow_up"
    )

    if is_follow_up:

        # -----------------------------------------------------
        # FOLLOW-UP
        # -----------------------------------------------------
        #
        # Stay on the SAME curriculum topic.
        #
        # Even if the LLM accidentally returns another
        # topic_day, the backend keeps the interview grounded.
        #

        selected_topic = current_topic

    else:

        # -----------------------------------------------------
        # MOVE TO NEXT TOPIC
        # -----------------------------------------------------

        if session.question_count > 0:
            selected_topic = move_to_next_topic(session)
        else:
            selected_topic = current_topic

        if selected_topic is None:
            selected_topic = current_topic

    # =========================================================
    # UPDATE CURRENT TOPIC
    # =========================================================

    session.current_topic_day = selected_topic.day
    session.current_topic_title = selected_topic.title

    # =========================================================
    # TRACK CURRICULUM COVERAGE
    # =========================================================

    if selected_topic.day not in session.covered_days:
        session.covered_days.append(
            selected_topic.day
        )

    # =========================================================
    # STORE INTERVIEWER QUESTION
    # =========================================================

    session.conversation.append(
        {
            "role": "assistant",
            "content": result.next_question,
        }
    )

    session.question_count += 1

    # =========================================================
    # COMPLETION GUARD
    # =========================================================
    #
    # For now, completion is only allowed when:
    #
    # 8+ questions
    # 4+ curriculum days
    #
    # Final feedback will be added in the next step.
    #

    if (
        session.question_count >= 8
        and len(session.covered_days) >= 4
    ):
        session.done = True

    session_manager.save_session(session)

    return InterviewResponse(
        reply=result.next_question,
        done=session.done,
        feedback=None,
    )