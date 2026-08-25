from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.endpoints import compatibility_router, router
from app.config import get_settings
from app.simulation.manager import SimulationManager


VERSION = "1.2.0"
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("kenkomirai.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    app.state.simulation_manager = SimulationManager(settings)
    logger.info("service_started environment=%s", settings.environment)
    yield
    logger.info("service_stopped")


app = FastAPI(
    title=settings.app_name,
    summary="Reproducible, safety-bounded urban outbreak scenario simulation",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1_000)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = request_id
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    logger.info(
        "request_completed method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
        request_id,
    )
    return response


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    logger.exception("unhandled_exception path=%s request_id=%s", request.url.path, request_id)
    return JSONResponse(status_code=500, content={"detail": "internal server error", "request_id": request_id})


@app.get("/", include_in_schema=False)
def service_index() -> dict[str, str]:
    return {
        "service": "kenkomirai-api",
        "version": VERSION,
        "health": f"{settings.api_prefix}/health",
        "documentation": "/docs",
    }


app.include_router(router)
app.include_router(compatibility_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
