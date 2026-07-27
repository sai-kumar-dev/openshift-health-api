"""Structured logging and per-application Prometheus metrics."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Info


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }
        for key in ("request_id", "method", "route", "status_code", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info and record.exc_info[0] is not None:
            payload["exception_type"] = record.exc_info[0].__name__
        return json.dumps(payload, separators=(",", ":"), ensure_ascii=True)


def configure_logging(name: str, level: int) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.handlers[:] = [handler]
    logger.setLevel(level)
    logger.propagate = False
    return logger


class Metrics:
    def __init__(self, service: str, version: str) -> None:
        self.registry = CollectorRegistry()
        self.info = Info("service", "Application build information", registry=self.registry)
        self.info.info({"name": service, "version": version})
        self.requests = Counter(
            "http_requests_total",
            "HTTP requests by method, route, and status class",
            ("method", "route", "status_class"),
            registry=self.registry,
        )
        self.duration = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration",
            ("method", "route"),
            registry=self.registry,
        )
        self.readiness = Gauge(
            "readiness_status",
            "Last readiness result (1 ready, 0 not ready)",
            registry=self.registry,
        )
        self.check_duration = Histogram(
            "readiness_check_duration_seconds",
            "Readiness check duration",
            ("check",),
            registry=self.registry,
        )
        self.check_failures = Counter(
            "readiness_check_failures_total",
            "Readiness check failures",
            ("check",),
            registry=self.registry,
        )
