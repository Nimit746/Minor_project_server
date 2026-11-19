import logging

from fastapi.encoders import jsonable_encoder

from app.utils.datetime_utils import _now

logger = logging.getLogger(__name__)

MAX_TRIES = 2


def _roadmap_state(session: dict) -> dict:
    """ADAPTER: input state for the roadmap graph (match Agentic_wf/.../roadmap/states/roadmap.py)."""
    turns = session.get("turns", []) or []
    weak_topics = list(session.get("weak_topics", []) or [])

    # Fallback: compute weak topics from turns where score < 7.0
    if not weak_topics and turns:
        weak_topics = list({
            t.get("topic") for t in turns
            if t.get("score") is not None and t["score"] < 7.0 and t.get("topic")
        })

    # Strengths: topics where score >= 8.0
    strengths = list({
        t.get("topic") for t in turns
        if t.get("score") is not None and t["score"] >= 8.0 and t.get("topic")
    })

    # If candidate scored high across all questions, target lowest scored topic for leveling up
    if not weak_topics and turns:
        sorted_turns = sorted(
            [t for t in turns if t.get("score") is not None and t.get("topic")],
            key=lambda t: t["score"]
        )
        if sorted_turns:
            weak_topics = [sorted_turns[0]["topic"]]

    is_universal = len(weak_topics) == 0

    return {
        "session_id": session["uuid"],
        "candidate_id": session["user_uuid"],
        "user_id": session["user_uuid"],
        "resume_id": session["resume_uuid"],
        "target_role": session.get("role"),          # aligned to Roadmap.target_role
        "company": session.get("target_company"),
        "weak_topics": weak_topics,
        "strengths": strengths,
        "performance_data": [session],
        "is_universal": is_universal,
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
