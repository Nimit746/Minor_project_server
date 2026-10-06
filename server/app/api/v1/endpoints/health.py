from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.api.deps import DB

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health(request: Request, db: DB):
    checks: dict[str, str] = {}
    try:
        await db.command("ping")
        checks["mongo"] = "ok"
    except Exception:
        checks["mongo"] = "down"

    arq = getattr(request.app.state, "arq", None)
    if arq is None:
        checks["redis"] = "unavailable"
    else:
        try:
            await arq.ping()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "down"

    checks["interview_graph"] = "loaded" if getattr(request.app.state, "interview_graph", None) else "missing"

    healthy = checks["mongo"] == "ok"  # Mongo is the hard dependency; the rest degrades gracefully
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={"status": "ok" if healthy else "degraded", "checks": checks},
    )
