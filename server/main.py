import logging
from contextlib import asynccontextmanager
from pathlib import Path

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.middleware import register_middleware
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.utils.graph_loader import load_graph

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

    # --- ARQ queue (optional at boot: API still starts if Redis is down) ---
    try:
        app.state.arq = await create_pool(RedisSettings.from_dsn(s.REDIS_URL))
    except Exception:
        logger.exception("Could not connect to Redis; upload/roadmap endpoints will return 503")
        app.state.arq = None

    yield

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
