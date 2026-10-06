from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AuthSvc
from app.core.exceptions import UnauthorizedException
from app.schemas.token_schema import RefreshRequest, TokenPair
from app.schemas.user_schema import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, service: AuthSvc):
    return await service.register(payload)


@router.post("/login", response_model=TokenPair)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], service: AuthSvc):
    user = await service.authenticate(form_data.username, form_data.password)
    if user is None:
        raise UnauthorizedException("Incorrect email or password")
    return service.issue_tokens(user)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, service: AuthSvc):
    return await service.refresh(payload.refresh_token)
