import logging

from fastapi.encoders import jsonable_encoder

from app.utils.datetime_utils import _now

logger = logging.getLogger(__name__)

MAX_TRIES = 2


def _roadmap_state(session: dict) -> dict:
    """ADAPTER: input state for the roadmap graph (match Agentic_wf/.../roadmap/states/roadmap.py)."""
    return {
        "session_id": session["uuid"],
        "user_id": session["user_uuid"],
        "resume_id": session["resume_uuid"],
        "role": session["role"],
        "company": session.get("target_company"),
    }


async def _set(col, roadmap_uuid: str, **fields) -> None:
    await col.update_one({"uuid": roadmap_uuid}, {"$set": {**fields, "updated_at": _now()}})


async def generate_roadmap(ctx: dict, roadmap_uuid: str) -> str:
    db = ctx["db"]
    col = db["roadmaps"]
    graph = ctx.get("roadmap_graph")

    roadmap = await col.find_one({"uuid": roadmap_uuid})
    if roadmap is None:
        return "missing"
    if graph is None:
        await _set(col, roadmap_uuid, status="failed", error="Roadmap engine unavailable")
        return "no_graph"
    session = await db["interview_sessions"].find_one({"uuid": roadmap["session_uuid"]})
    if session is None:
        await _set(col, roadmap_uuid, status="failed", error="Interview session not found")
        return "no_session"

    await _set(col, roadmap_uuid, status="processing", error=None)
    try:
        out = await graph.ainvoke(_roadmap_state(session))
    except Exception as exc:
        logger.exception("generate_roadmap failed for %s", roadmap_uuid)
        if ctx.get("job_try", 1) >= MAX_TRIES:
            await _set(col, roadmap_uuid, status="failed", error=f"{type(exc).__name__}: generation failed")
        raise

    content = out.get("roadmap") if isinstance(out, dict) and out.get("roadmap") else out
    content = jsonable_encoder(content)  # make LangGraph/Pydantic output BSON-safe
    if not isinstance(content, dict):
        content = {"result": content}
    await _set(col, roadmap_uuid, status="ready", content=content)
    return "ready"
