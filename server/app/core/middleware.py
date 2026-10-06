import uuid
import time
import logging
from fastapi import FastAPI, Request
logger = logging.getLogger("app.requests")

def register_middleware(app: FastAPI) -> None:
    @app.middleware('http')
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        logger.info(
            "%s %s -> %s (%.1fms) rid=%s",
            request.method, request.url.path, response.status_code, duration_ms, request_id,
        )
        return response