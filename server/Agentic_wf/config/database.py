from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.database import Database
from Agentic_wf.config.settings import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

_async_client: AsyncIOMotorClient | None = None
_sync_client: MongoClient | None = None


def get_async_client() -> AsyncIOMotorClient:
    """Get or create singleton AsyncIOMotorClient."""
    global _async_client
    if _async_client is None:
        uri = settings.mongo_uri
        logger.info(f"Connecting AsyncIOMotorClient to {uri}")
        _async_client = AsyncIOMotorClient(uri)
    return _async_client


def get_async_db() -> AsyncIOMotorDatabase:
    """Get async MongoDB database instance."""
    client = get_async_client()
    return client[settings.mongo_db_name]


def get_sync_client() -> MongoClient:
    """Get or create singleton sync MongoClient."""
    global _sync_client
    if _sync_client is None:
        uri = settings.mongo_uri
        _sync_client = MongoClient(uri)
    return _sync_client


def get_db() -> AsyncIOMotorDatabase:
    """Default get_db returns the async database for LangGraph async nodes."""
    return get_async_db()


def get_sync_db() -> Database:
    """Get synchronous MongoDB database instance."""
    client = get_sync_client()
    return client[settings.mongo_db_name]
