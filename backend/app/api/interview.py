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


# =========================================================
# TOPIC HELPERS
# =========================================================

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


def get_next_uncovered_topic(session):
    """
    Find the next planned topic whose curriculum day
    has not yet been covered.
    """

    topics = get_all_planned_topics(session.plan)

    for index, topic in enumerate(topics):

        if topic.day not in session.covered_days:
            session.current_topic_index = index
            return topic

    return None


# =========================================================
# CONVERSATION HELPER
# =========================================================

def build_conversation(session):
    """Convert stored conversation messages into LLM format."""

    return [
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


# =========================================================
# FEEDBACK HELPER
# =========================================================

def generate_final_feedback(
    session,
    latest_answer,
):
    """
    Generate final interview feedback after the candidate
    has answered the eighth question.
    """

    current_topic = get_current_topic(session)

    if current_topic is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to determine current topic "
                "for final feedback."
            ),
        )

    curriculum_day = curriculum_service.get_day(
        current_topic.day
    )

    if curriculum_day is None:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Curriculum day {current_topic.day} "
                "could not be found."
            ),
        )

    conversation = build_conversation(session)

    context = context_builder.build(
        profile=session.profile,
        plan=session.plan,
        curriculum_day=curriculum_day,
        conversation=conversation,
        question_number=session.question_count,
        covered_days=session.covered_days,
        latest_answer=latest_answer,
    )

    feedback = llm_service.generate_feedback(
        system_prompt=INTERVIEWER_SYSTEM_PROMPT,
        context=context,
    )

    return feedback


# =========================================================
# INTERVIEW ENDPOINT
# =========================================================

@router.post(
    "/interview",
    response_model=InterviewResponse,
)
def interview(
    request: InterviewRequest,
):

    # =====================================================
    # CREATE / RESTORE SESSION
    # =====================================================

    session = session_manager.get_session(
        request.sessionId
    )

    if session is None:

        # Candidate is required only for the first request.
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

        # -------------------------------------------------
        # LOAD CANDIDATE
        # -------------------------------------------------

        candidate = candidate_service.get_candidate(
            candidate_id
        )

        if candidate is None:
            raise HTTPException(
                status_code=404,
                detail="Candidate not found.",
            )

        # -------------------------------------------------
        # ANALYZE CANDIDATE
        # -------------------------------------------------

        profile = candidate_analyzer.analyze(
            candidate
        )

        # -------------------------------------------------
        # CREATE PERSONALIZED PLAN
        # -------------------------------------------------

        plan = interview_planner.create_plan(
            profile
        )

        # -------------------------------------------------
        # CREATE SESSION
        # -------------------------------------------------

        session = session_manager.create_session(
            session_id=request.sessionId,
            candidate_id=candidate.member.id,
            candidate_name=candidate.member.name,
            profile=profile,
            plan=plan,
        )

    # =====================================================
    # SAFETY CHECK
    # =====================================================

    if session.done:

        return InterviewResponse(
            reply=(
                "This interview has already been completed."
            ),
            done=True,
            feedback=None,
        )

    # =====================================================
    # ADD CANDIDATE ANSWER TO CONVERSATION
    # =====================================================

    if request.message:

        session.conversation.append(
            {
                "role": "user",
                "content": request.message,
            }
        )

    # =====================================================
    # IMPORTANT COMPLETION CHECK
    # =====================================================
    #
    # If question_count is already 8 when a new message
    # arrives, that message is the candidate's answer
    # to Question 8.
    #
    # Therefore:
    #
    # Q8 is NOT generated again.
    # Q8 has already been shown.
    # The candidate has now answered it.
    # Generate final feedback.
    #
    # =====================================================

    if (
        request.message
        and session.question_count >= 8
        and len(session.covered_days) >= 4
    ):

        feedback = generate_final_feedback(
            session=session,
            latest_answer=request.message,
        )

        session.done = True

        session_manager.save_session(
            session
        )

        return InterviewResponse(
            reply=(
                "Thank you. That concludes the "
                "technical interview."
            ),
            done=True,
            feedback={
                "summary": feedback.summary,
                "strengths": feedback.strengths,
                "gaps": feedback.gaps,
                "next": feedback.next,
            },
        )

    # =====================================================
    # SELECT TOPIC FOR THIS TURN
    # =====================================================

    MAX_FOLLOW_UPS_PER_TOPIC = 2

    current_topic = get_current_topic(
        session
    )

    if current_topic is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Interview plan contains no topics."
            ),
        )

    # -----------------------------------------------------
    # FIRST QUESTION
    # -----------------------------------------------------

    if session.question_count == 0:

        selected_topic = current_topic

        session.follow_ups_on_current_topic = 0

    # -----------------------------------------------------
    # SUBSEQUENT QUESTIONS
    # -----------------------------------------------------

    else:

        # =================================================
        # FORCE FOUR DIFFERENT CURRICULUM DAYS FIRST
        # =================================================

        if len(session.covered_days) < 4:

            uncovered_topic = (
                get_next_uncovered_topic(session)
            )

            if uncovered_topic is not None:

                selected_topic = uncovered_topic

                session.follow_ups_on_current_topic = 0

            else:

                selected_topic = current_topic

        # =================================================
        # AFTER FOUR DAYS ARE COVERED
        # =================================================

        else:

            # -------------------------------------------------
            # ALLOW LIMITED FOLLOW-UPS
            # -------------------------------------------------

            if (
                session.follow_ups_on_current_topic
                < MAX_FOLLOW_UPS_PER_TOPIC
            ):

                selected_topic = current_topic

                session.follow_ups_on_current_topic += 1

            # -------------------------------------------------
            # MOVE TO NEXT TOPIC
            # -------------------------------------------------

            else:

                selected_topic = (
                    move_to_next_topic(
                        session
                    )
                )

                session.follow_ups_on_current_topic = 0

                # Safety fallback.
                if selected_topic is None:
                    selected_topic = current_topic

    # =====================================================
    # UPDATE CURRENT TOPIC
    # =====================================================

    session.current_topic_day = (
        selected_topic.day
    )

    session.current_topic_title = (
        selected_topic.title
    )

    # =====================================================
    # TRACK CURRICULUM COVERAGE
    # =====================================================

    if selected_topic.day not in session.covered_days:

        session.covered_days.append(
            selected_topic.day
        )

    # =====================================================
    # GET CURRICULUM FOR SELECTED TOPIC
    # =====================================================

    curriculum_day = curriculum_service.get_day(
        selected_topic.day
    )

    if curriculum_day is None:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Curriculum day {selected_topic.day} "
                "could not be found."
            ),
        )

    # =====================================================
    # BUILD CONVERSATION
    # =====================================================

    conversation = build_conversation(
        session
    )

    # =====================================================
    # LATEST CANDIDATE ANSWER
    # =====================================================

    latest_answer = (
        request.message
        if request.message
        else None
    )

    # =====================================================
    # BUILD LLM CONTEXT
    # =====================================================

    context = context_builder.build(
        profile=session.profile,
        plan=session.plan,
        curriculum_day=curriculum_day,
        conversation=conversation,
        question_number=(
            session.question_count + 1
        ),
        covered_days=session.covered_days,
        latest_answer=latest_answer,
    )

    # =====================================================
    # ASK GROQ
    # =====================================================

    result = llm_service.generate_interview_turn(
        system_prompt=INTERVIEWER_SYSTEM_PROMPT,
        context=context,
    )

    # =====================================================
    # STORE INTERVIEWER QUESTION
    # =====================================================

    session.conversation.append(
        {
            "role": "assistant",
            "content": result.next_question,
        }
    )

    # =====================================================
    # INCREMENT QUESTION COUNT
    # =====================================================

    session.question_count += 1

    # =====================================================
    # IMPORTANT:
    # NEVER COMPLETE HERE.
    #
    # If this is Question 8, return Question 8 to
    # the candidate with done=False.
    #
    # Completion happens when the candidate sends
    # the answer to Question 8 on the next request.
    # =====================================================

    session_manager.save_session(
        session
    )

    return InterviewResponse(
        reply=result.next_question,
        done=False,
        feedback=None,
    )