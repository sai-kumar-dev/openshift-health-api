"""Validated application configuration."""

from __future__ import annotations

import logging
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

VERSION = "0.3.0"


class ConfigurationError(ValueError):
    """Raised when environment configuration is unsafe or invalid."""


def _integer(env: dict[str, str], name: str, default: int, minimum: int, maximum: int) -> int:
    raw = env.get(name, str(default))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer") from exc
    if not minimum <= value <= maximum:
        raise ConfigurationError(f"{name} must be between {minimum} and {maximum}")
    return value


def _float(env: dict[str, str], name: str, default: float, minimum: float, maximum: float) -> float:
    raw = env.get(name, str(default))
    try:
        value = float(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be numeric") from exc
    if not minimum <= value <= maximum:
        raise ConfigurationError(f"{name} must be between {minimum} and {maximum}")
    return value


def _boolean(env: dict[str, str], name: str, default: bool = False) -> bool:
    raw = env.get(name, str(default)).strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} must be true or false")


def _dependency_url(env: dict[str, str], name: str, enabled: bool, schemes: set[str]) -> str | None:
    value = env.get(name)
    if not enabled:
        return value
    if not value:
        raise ConfigurationError(f"{name} is required when its check is enabled")
    parsed = urlsplit(value)
    if parsed.scheme not in schemes or not parsed.hostname:
        raise ConfigurationError(f"{name} must be a valid supported URL")
    return value


@dataclass(frozen=True, slots=True)
class Settings:
    service_name: str
    version: str
    log_level: int
    min_free_disk_mb: int
    disk_check_path: Path
    dependency_timeout_seconds: float
    postgres_enabled: bool
    postgres_url: str | None
    redis_enabled: bool
    redis_url: str | None
    metrics_enabled: bool

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> Settings:
        env = dict(os.environ if environ is None else environ)
        level_name = env.get("LOG_LEVEL", "INFO").upper()
        level = logging.getLevelNamesMapping().get(level_name)
        if not isinstance(level, int):
            raise ConfigurationError("LOG_LEVEL must be a standard Python log level")
        postgres_enabled = _boolean(env, "POSTGRES_CHECK_ENABLED")
        redis_enabled = _boolean(env, "REDIS_CHECK_ENABLED")
        return cls(
            service_name=env.get("SERVICE_NAME", "openshift-health-api"),
            version=env.get("SERVICE_VERSION", VERSION),
            log_level=level,
            min_free_disk_mb=_integer(env, "MIN_FREE_DISK_MB", 64, 0, 1_048_576),
            disk_check_path=Path(env.get("DISK_CHECK_PATH", tempfile.gettempdir())),
            dependency_timeout_seconds=_float(env, "DEPENDENCY_TIMEOUT_SECONDS", 1.0, 0.05, 30.0),
            postgres_enabled=postgres_enabled,
            postgres_url=_dependency_url(
                env, "POSTGRES_URL", postgres_enabled, {"postgres", "postgresql"}
            ),
            redis_enabled=redis_enabled,
            redis_url=_dependency_url(env, "REDIS_URL", redis_enabled, {"redis", "rediss"}),
            metrics_enabled=_boolean(env, "METRICS_ENABLED", True),
        )
