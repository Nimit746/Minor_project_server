from fastapi import APIRouter, status

from app.api.deps import CurrentUser, InterviewSvc, Pagination
from app.schemas.interview_schema import (
    AnswerSubmit,
    InterviewCreate,
    InterviewRead,
    InterviewSummary,
    InterviewTurnResponse,
)

router = APIRouter(prefix="/interviews", tags=["Interviews"])


@router.post("", response_model=InterviewTurnResponse, status_code=status.HTTP_201_CREATED)
async def start_interview(payload: InterviewCreate, user: CurrentUser, service: InterviewSvc):
    """Starts a session and returns the first question."""
    return await service.start(user, payload)


@router.get("", response_model=list[InterviewSummary])
async def list_interviews(user: CurrentUser, service: InterviewSvc, page: Pagination):
    return await service.list_for_user(user, page.skip, page.limit)


@router.get("/{session_uuid}", response_model=InterviewRead)
async def get_interview(session_uuid: str, user: CurrentUser, service: InterviewSvc):
    return await service.get(user, session_uuid)


@router.post("/{session_uuid}/answer", response_model=InterviewTurnResponse)
async def submit_answer(session_uuid: str, payload: AnswerSubmit, user: CurrentUser, service: InterviewSvc):
    """Submits the answer to question `seq`; returns the next question or the final summary."""
    return await service.answer(user, session_uuid, payload.seq, payload.answer)


@router.post("/{session_uuid}/abandon", response_model=InterviewRead)
async def abandon_interview(session_uuid: str, user: CurrentUser, service: InterviewSvc):
    return await service.abandon(user, session_uuid)
