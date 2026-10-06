from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.security import OAuth2PasswordBearer
from pymongo.asynchronous.database import AsyncDatabase

from app.config.settings import get_settings
from app.core.exceptions import ForbiddenException, ServiceUnavailableException, UnauthorizedException
from app.core.security import decode_token
from app.db.base_repository import BaseRepository
from app.db.mongodb import get_database
from app.models.user_model import UserModel
from app.services.auth_service import AuthService
from app.services.interview_service import InterviewService
from app.services.resume_service import ResumeService
from app.services.roadmap_service import RoadmapService
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{get_settings().API_V1_PREFIX}/auth/login")


# ---------------- infrastructure ----------------
def get_db() -> AsyncDatabase:
    return get_database()


DB = Annotated[AsyncDatabase, Depends(get_db)]


def get_arq(request: Request):
    pool = getattr(request.app.state, "arq", None)
    if pool is None:
        raise ServiceUnavailableException("Job queue is not available")
    return pool


# ---------------- auth ----------------
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DB) -> UserModel:
    payload = decode_token(token, expected_type="access")
    user = await BaseRepository(db["users"], UserModel).get_by_uuid(payload["sub"])
    if user is None or not user.is_active:
        raise UnauthorizedException("User not found or inactive")
    return user


CurrentUser = Annotated[UserModel, Depends(get_current_user)]


def require_roles(*allowed_roles: str):
    """RBAC guard factory: Depends(require_roles("admin"))."""

    async def checker(user: CurrentUser) -> UserModel:
        if not set(user.roles) & set(allowed_roles):
            raise ForbiddenException()
        return user

    return checker


# ---------------- pagination ----------------
@dataclass
class PaginationParams:
    skip: int
    limit: int


def pagination_params(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),  # bounded: never let a client request an unbounded cursor
) -> PaginationParams:
    return PaginationParams(skip=skip, limit=limit)


Pagination = Annotated[PaginationParams, Depends(pagination_params)]


# ---------------- service providers ----------------
def get_auth_service(db: DB) -> AuthService:
    return AuthService(db)


def get_user_service(db: DB) -> UserService:
    return UserService(db)


def get_resume_service(db: DB, request: Request) -> ResumeService:
    return ResumeService(db, get_arq(request))


def get_interview_service(db: DB, request: Request) -> InterviewService:
    graph = getattr(request.app.state, "interview_graph", None)
    if graph is None:
        raise ServiceUnavailableException("Interview engine is not available")
    return InterviewService(db, graph)


def get_roadmap_service(db: DB, request: Request) -> RoadmapService:
    return RoadmapService(db, get_arq(request))


AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
UserSvc = Annotated[UserService, Depends(get_user_service)]
ResumeSvc = Annotated[ResumeService, Depends(get_resume_service)]
InterviewSvc = Annotated[InterviewService, Depends(get_interview_service)]
RoadmapSvc = Annotated[RoadmapService, Depends(get_roadmap_service)]
