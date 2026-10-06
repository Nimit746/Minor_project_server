from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from pymongo import ReturnDocument
from pymongo.asynchronous.collection import AsyncCollection

from app.utils.datetime_utils import _now

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    """Generic CRUD wrapper around a single Mongo collection.

    Public identifier is always the `uuid` field, never Mongo's `_id`.
    """

    def __init__(self, collection: AsyncCollection, model_cls: type[ModelT]):
        self.collection = collection
        self.model_cls = model_cls

    def _to_model(self, doc: dict[str, Any]) -> ModelT:
        return self.model_cls.model_validate(doc)  # unknown keys (like _id) are ignored

    async def create(self, data: BaseModel | dict[str, Any]) -> ModelT:
        doc = data.model_dump() if isinstance(data, BaseModel) else dict(data)
        await self.collection.insert_one(doc)  # may raise DuplicateKeyError
        return self._to_model(doc)

    async def get_by_uuid(self, uuid_str: str) -> ModelT | None:
        doc = await self.collection.find_one({"uuid": uuid_str})
        return self._to_model(doc) if doc else None

    async def get_one(self, filters: dict[str, Any]) -> ModelT | None:
        doc = await self.collection.find_one(filters)
        return self._to_model(doc) if doc else None

    async def find_many(
        self,
        filters: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 20,
        sort: list[tuple[str, int]] | None = None,
        projection: dict[str, int] | None = None,
    ) -> list[ModelT]:
        cursor = self.collection.find(filters or {}, projection)
        cursor = cursor.sort(sort or [("created_at", -1)]).skip(skip).limit(limit)
        return [self._to_model(doc) async for doc in cursor]

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        return await self.collection.count_documents(filters or {})

    async def update_by_uuid(self, uuid_str: str, data: dict[str, Any]) -> ModelT | None:
        doc = await self.collection.find_one_and_update(
            {"uuid": uuid_str},
            {"$set": {**data, "updated_at": _now()}},
            return_document=ReturnDocument.AFTER,
        )
        return self._to_model(doc) if doc else None

    async def delete_by_uuid(self, uuid_str: str) -> bool:
        result = await self.collection.delete_one({"uuid": uuid_str})
        return result.deleted_count == 1
