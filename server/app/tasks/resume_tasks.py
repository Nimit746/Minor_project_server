import logging

from app.utils.datetime_utils import _now

logger = logging.getLogger(__name__)

MAX_TRIES = 3


def _resume_state(doc: dict) -> dict:
    """ADAPTER: input state for the resume_parse graph (match Agentic_wf/.../resume_parse/states/file.py)."""
    return {
        "document_id": doc["uuid"],
        "resume_id": doc["uuid"],
        "user_id": doc["user_uuid"],
        "event_id": f"evt_{doc['uuid']}",
        "file_url": doc.get("file_path", ""),
        "filename": doc["filename"],
        "file_name": doc["filename"],
        "file_type": doc["content_type"],
        "status": "pending",
        "documents": [],
        "chunks": [],
        "metadata": {
            "local_temp_path": doc["file_path"],
        },
        "error": None,
    }


async def _set(col, resume_uuid: str, **fields) -> None:
    await col.update_one({"uuid": resume_uuid}, {"$set": {**fields, "updated_at": _now()}})


async def ingest_resume(ctx: dict, resume_uuid: str) -> str:
    """ARQ job: run the resume_parse graph (load -> chunk -> metadata -> store)."""
    col = ctx["db"]["resumes"]
    graph = ctx.get("resume_graph")

    doc = await col.find_one({"uuid": resume_uuid})
    if doc is None:
        logger.warning("ingest_resume: resume %s no longer exists", resume_uuid)
        return "missing"
    if graph is None:
        await _set(col, resume_uuid, status="failed", error="Resume processing engine unavailable")
        return "no_graph"  # retrying won't help

    await _set(col, resume_uuid, status="processing", error=None)
    try:
        result = await graph.ainvoke(_resume_state(doc))
        if result and (result.get("error") or str(result.get("status", "")).endswith("_failed")):
            err_msg = result.get("error") or f"Processing failed (status: {result.get('status')})"
            logger.error("ingest_resume pipeline error for %s: %s", resume_uuid, err_msg)
            await _set(col, resume_uuid, status="failed", error=err_msg)
            return "failed"
    except Exception as exc:
        logger.exception("ingest_resume failed for %s (try %s)", resume_uuid, ctx.get("job_try"))
        if ctx.get("job_try", 1) >= MAX_TRIES:
            await _set(col, resume_uuid, status="failed", error=f"{type(exc).__name__}: processing failed")
        raise  # lets ARQ retry with backoff
    await _set(col, resume_uuid, status="ready")
    return "ready"
