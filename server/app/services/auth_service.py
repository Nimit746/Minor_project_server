import asyncio

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    dummy_hash,
    hash_password,
    verify_password,
)
from app.db.base_repository import BaseRepository
from app.models.user_model import UserModel
from app.schemas.token_schema import TokenPair
from app.schemas.user_schema import UserCreate


class AuthService:
    def __init__(self, db: AsyncDatabase):
        self.users = BaseRepository(db["users"], UserModel)

    async def register(self, payload: UserCreate) -> UserModel:
        email = payload.email.lower()
        if await self.users.get_one({"email": email}):
            raise ConflictException("An account with this email already exists")
        user = UserModel(
            email=email,
            full_name=payload.full_name.strip(),
            hashed_password=await asyncio.to_thread(hash_password, payload.password),
        )
        try:
            return await self.users.create(user)
        except DuplicateKeyError:  # race between the check above and the insert
            raise ConflictException("An account with this email already exists")

    async def authenticate(self, email: str, password: str) -> UserModel | None:
        user = await self.users.get_one({"email": email.lower()})
        if user is None:
            # burn the same CPU time so response timing doesn't reveal which emails exist
            await asyncio.to_thread(verify_password, password, dummy_hash())
            return None
        ok = await asyncio.to_thread(verify_password, password, user.hashed_password)
        if not ok or not user.is_active:
            return None
        return user

    @staticmethod
    def issue_tokens(user: UserModel) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(user.uuid, {"roles": user.roles}),
            refresh_token=create_refresh_token(user.uuid),
        )

    async def refresh(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token, expected_type="refresh")
        user = await self.users.get_by_uuid(payload["sub"])
        if user is None or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
        return self.issue_tokens(user)
