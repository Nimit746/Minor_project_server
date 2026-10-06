"""ARQ worker.  Run with:  uv run arq app.tasks.worker.WorkerSettings

The worker must see the same UPLOAD_DIR as the API (same machine / shared volume).
On Windows run it inside WSL2 or Docker (ARQ targets POSIX).
"""
import logging

from arq.connections import RedisSettings
from pymongo import AsyncMongoClient

from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.tasks.resume_tasks import MAX_TRIES, ingest_resume
from app.tasks.roadmap_tasks import generate_roadmap
from app.utils.graph_loader import load_graph

logger = logging.getLogger(__name__)


async def on_startup(ctx: dict) -> None:
    s = get_settings()
    setup_logging(s.LOG_LEVEL)
    client = AsyncMongoClient(s.MONGO_URI, uuidRepresentation="standard", tz_aware=True)
    ctx["mongo_client"] = client
    ctx["db"] = client[s.MONGODB_DB_NAME]  # rename if your DB-name field differs
    ctx["resume_graph"] = load_graph(
        "Agentic_wf.agents.resume_parse.graph_builder",
        factory="build_ingestion_graph",
    )
    ctx["roadmap_graph"] = load_graph(
        "Agentic_wf.agents.roadmap.graph_builder",
        factory="build_roadmap_graph",
    )
    logger.info("Worker ready (resume_graph=%s, roadmap_graph=%s)",
                bool(ctx["resume_graph"]), bool(ctx["roadmap_graph"]))


async def on_shutdown(ctx: dict) -> None:
    client = ctx.get("mongo_client")
    if client is not None:
        await client.close()


class WorkerSettings:
    functions = [ingest_resume, generate_roadmap]
    on_startup = on_startup
    on_shutdown = on_shutdown
    redis_settings = RedisSettings.from_dsn(get_settings().REDIS_URL)
    max_tries = MAX_TRIES
    job_timeout = 600  # seconds
    keep_result = 3600