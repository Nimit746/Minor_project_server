from pymongo.asynchronous.database import AsyncDatabase

from app.core.exceptions import NotFoundException
from app.db.base_repository import BaseRepository
from app.models.user_model import UserModel
from app.schemas.user_schema import UserUpdate


class UserService:
    def __init__(self, db: AsyncDatabase):
        self.repo = BaseRepository(db["users"], UserModel)

    async def get_by_uuid(self, user_uuid: str) -> UserModel:
        user = await self.repo.get_by_uuid(user_uuid)
        if user is None:
            raise NotFoundException("User")
        return user

    async def update_me(self, user_uuid: str, payload: UserUpdate) -> UserModel:
        data = payload.model_dump(exclude_unset=True)  # only what the client actually sent
        if not data:
            return await self.get_by_uuid(user_uuid)
        updated = await self.repo.update_by_uuid(user_uuid, data)
        if updated is None:
            raise NotFoundException("User")
        return updated
