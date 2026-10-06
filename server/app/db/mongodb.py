import logging

from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.config.settings import get_settings

logger = logging.getLogger(__name__)


class MongoManager:
    """Holds the single client for the app's lifetime."""

    client: AsyncMongoClient | None = None
    db: AsyncDatabase | None = None


mongo = MongoManager()


async def connect_to_mongo() -> None:
    s = get_settings()
    mongo.client = AsyncMongoClient(
        s.MONGO_URI,
        uuidRepresentation="standard",
        tz_aware=True,  # datetimes come back timezone-aware (matches _now())
        serverSelectionTimeoutMS=5000,
    )
    mongo.db = mongo.client[s.MONGODB_DB_NAME]
    await mongo.client.admin.command("ping")  # fail fast on bad URI/credentials
    await ensure_indexes(mongo.db)
    logger.info("Connected to MongoDB database '%s'", s.MONGODB_DB_NAME)


async def close_mongo_connection() -> None:
    if mongo.client is not None:
        await mongo.client.close()
        mongo.client = None
        mongo.db = None


async def ensure_indexes(db: AsyncDatabase) -> None:
    """Idempotent. Add one line per new collection/query pattern."""
    await db["users"].create_index("email", unique=True)
    await db["users"].create_index("uuid", unique=True)

    await db["resumes"].create_index("uuid", unique=True)
    await db["resumes"].create_index([("user_uuid", 1), ("created_at", -1)])

    await db["interview_sessions"].create_index("uuid", unique=True)
    await db["interview_sessions"].create_index([("user_uuid", 1), ("created_at", -1)])
    await db["interview_sessions"].create_index([("user_uuid", 1), ("status", 1)])

    await db["roadmaps"].create_index("uuid", unique=True)
    await db["roadmaps"].create_index("session_uuid", unique=True)
    await db["roadmaps"].create_index([("user_uuid", 1), ("created_at", -1)])


def get_database() -> AsyncDatabase:
    if mongo.db is None:
        raise RuntimeError("MongoDB is not connected (lifespan did not run?)")
    return mongo.db
