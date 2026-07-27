"""FastAPI application factory."""

from __future__ import annotations

import platform
import re
import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.checks import run_readiness_checks
from app.config import Settings
from app.observability import Metrics, configure_logging

REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


def _request_id(value: str | None) -> str:
    return value if value and REQUEST_ID_PATTERN.fullmatch(value) else str(uuid.uuid4())


def _problem(status_code: int, title: str, request_id: str) -> JSONResponse:
    return JSONResponse(
        {"type": "about:blank", "title": title, "status": status_code, "request_id": request_id},
        status_code=status_code,
        media_type="application/problem+json",
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings.from_env()
    logger = configure_logging(config.service_name, config.log_level)
    metrics = Metrics(config.service_name, config.version)
    started_at = time.monotonic()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        logger.info("service_started")
        yield
        logger.info("service_stopped")

    application = FastAPI(
        title="OpenShift-Ready Service Health API",
        version=config.version,
        description="Health, readiness, diagnostics, and observability for an OpenShift service.",
        lifespan=lifespan,
    )
    application.state.settings = config
    application.state.metrics = metrics

    @application.middleware("http")
    async def request_context(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = _request_id(request.headers.get("X-Request-ID"))
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed",
                extra={"request_id": request_id, "method": request.method, "route": "unmatched"},
            )
            response = _problem(500, "Internal Server Error", request_id)
        route = request.scope.get("route")
        template = getattr(route, "path", "unmatched")
        duration = time.perf_counter() - started
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        if config.metrics_enabled:
            status_class = f"{response.status_code // 100}xx"
            metrics.requests.labels(request.method, template, status_class).inc()
            metrics.duration.labels(request.method, template).observe(duration)
        logger.info(
            "request_completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "route": template,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 3),
            },
        )
        return response

    @application.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        title = "Not Found" if exc.status_code == 404 else "Request Failed"
        return _problem(exc.status_code, title, request.state.request_id)

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, _: RequestValidationError) -> JSONResponse:
        return _problem(422, "Request Validation Failed", request.state.request_id)

    @application.get("/healthz", tags=["platform"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok", "service": config.service_name, "version": config.version}

    @application.get("/readyz", tags=["platform"])
    async def readyz() -> JSONResponse:
        checks = await run_readiness_checks(config)
        ready = all(check.ok for check in checks)
        if config.metrics_enabled:
            metrics.readiness.set(1 if ready else 0)
            for check in checks:
                metrics.check_duration.labels(check.name).observe(check.duration_seconds)
                if not check.ok:
                    metrics.check_failures.labels(check.name).inc()
        return JSONResponse(
            {"status": "ready" if ready else "not_ready", "checks": [c.to_dict() for c in checks]},
            status_code=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    @application.get("/api/v1/system", tags=["diagnostics"])
    async def system_info() -> dict[str, object]:
        return {
            "service": config.service_name,
            "version": config.version,
            "python": platform.python_version(),
            "platform": platform.system(),
            "architecture": platform.machine(),
            "uptime_seconds": round(time.monotonic() - started_at, 3),
        }

    @application.get("/metrics", tags=["platform"])
    async def prometheus_metrics() -> Response:
        if not config.metrics_enabled:
            return Response(status_code=404)
        return Response(
            generate_latest(metrics.registry), headers={"Content-Type": CONTENT_TYPE_LATEST}
        )

    return application


app = create_app()
