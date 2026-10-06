from fastapi import APIRouter

from app.api.deps import CurrentUser, UserSvc
from app.schemas.user_schema import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def read_me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserRead)
async def update_me(payload: UserUpdate, user: CurrentUser, service: UserSvc):
    return await service.update_me(user.uuid, payload)
