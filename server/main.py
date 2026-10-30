import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from arq import create_pool
from arq.connections import RedisSettings
from arq.worker import Worker, create_worker
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import register_middleware
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.utils.graph_loader import load_graph

from app.tasks.worker import WorkerSettings

logger = logging.getLogger(__name__)


def _build_checkpointer(sync_client):
    """Persistent LangGraph checkpointer so interrupt/resume survives restarts and multiple workers."""
    s = get_settings()
    try:
        from langgraph.checkpoint.mongodb import MongoDBSaver

        return MongoDBSaver(sync_client, db_name=s.MONGODB_DB_NAME)
    except Exception:
        logger.exception("MongoDBSaver unavailable - falling back to IN-MEMORY checkpoints "
                         "(interviews will be lost on restart; fine for dev only)")
        from langgraph.checkpoint.memory import MemorySaver

        return MemorySaver()


def _log_worker_exit(task: asyncio.Task) -> None:
    """Surface a crashed in-process worker in the logs instead of failing silently."""
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error("In-process ARQ worker stopped unexpectedly", exc_info=exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    setup_logging(s.LOG_LEVEL)
    Path(s.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    # --- MongoDB (async, used by request handlers) ---
    await connect_to_mongo()

    # --- LangGraph engine: compiled once, shared by all requests ---
    from pymongo import MongoClient

    sync_client = MongoClient(s.MONGO_URI, uuidRepresentation="standard", tz_aware=True)
    app.state.interview_graph = load_graph(
        "Agentic_wf.agents.generate_questions.graph_builder",
        factory="build_question_generator_graph",
        checkpointer=_build_checkpointer(sync_client),
    )

    # --- ARQ queue + in-process worker ---
    # Render charges for Background Workers, so the worker runs inside this web
    # service. It consumes the same Redis queue the upload endpoint writes to.
    worker: Worker | None = None
    worker_task: asyncio.Task | None = None
    try:
        redis_settings = RedisSettings.from_dsn(s.REDIS_URL)
        app.state.arq = await create_pool(redis_settings)

        # Reuses app/tasks/worker.py: its on_startup builds ctx["db"], ctx["resume_graph"]
        # and ctx["roadmap_graph"], which ingest_resume / generate_roadmap need.
        worker = create_worker(
            WorkerSettings,
            handle_signals=False,  # uvicorn owns SIGTERM/SIGINT
            max_jobs=1,            # one job at a time keeps memory low
        )
        worker_task = asyncio.create_task(worker.async_run(), name="arq-worker")
        worker_task.add_done_callback(_log_worker_exit)
        logger.info("In-process ARQ worker started with functions: %s",
                    [f.__name__ for f in WorkerSettings.functions])
    except Exception:
        logger.exception("Could not connect to Redis; upload/roadmap endpoints will return 503")
        app.state.arq = None

    yield

    # --- shutdown ---
    if worker is not None:
        await worker.close()
    if worker_task is not None:
        worker_task.cancel()
    if getattr(app.state, "arq", None) is not None:
        await app.state.arq.aclose()
    sync_client.close()
    await close_mongo_connection()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(
        title=s.APP_NAME,
        debug=s.DEBUG,
        lifespan=lifespan,
        docs_url=None if s.is_production else "/docs",
        redoc_url=None if s.is_production else "/redoc",
        openapi_url=None if s.is_production else "/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=s.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_middleware(app)
    register_exception_handlers(app)
    app.include_router(api_router, prefix=s.API_V1_PREFIX)

    @app.get("/healthz", include_in_schema=False)
    async def liveness():  # cheap liveness probe for Docker/K8s (no DB access)
        return {"status": "alive"}

    return app


app = create_app()