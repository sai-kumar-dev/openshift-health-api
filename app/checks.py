"""Bounded, safe readiness checks."""

from __future__ import annotations

import asyncio
import os
import shutil
from collections.abc import Awaitable
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from urllib.parse import urlsplit

from app.config import Settings


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    duration_seconds: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


async def check_temp_directory(path: Path) -> CheckResult:
    started = perf_counter()
    probe = path / f".health-{os.getpid()}-{id(path)}"
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe.write_text("ok", encoding="utf-8")
        return CheckResult("temp_directory", True, "writable", perf_counter() - started)
    except OSError:
        return CheckResult("temp_directory", False, "unavailable", perf_counter() - started)
    finally:
        try:
            probe.unlink(missing_ok=True)
        except OSError:
            pass


async def check_disk_space(path: Path, minimum_mb: int) -> CheckResult:
    started = perf_counter()
    try:
        free_mb = shutil.disk_usage(path).free // (1024 * 1024)
        ok = free_mb >= minimum_mb
        return CheckResult(
            "disk_space",
            ok,
            "sufficient" if ok else "insufficient",
            perf_counter() - started,
        )
    except OSError:
        return CheckResult("disk_space", False, "unavailable", perf_counter() - started)


async def check_tcp_dependency(
    name: str, url: str, timeout: float, default_port: int
) -> CheckResult:
    """Check dependency reachability without exposing its address or credentials."""
    started = perf_counter()
    parsed = urlsplit(url)
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(parsed.hostname, parsed.port or default_port),
            timeout=timeout,
        )
        del reader
        writer.close()
        await writer.wait_closed()
        return CheckResult(name, True, "reachable", perf_counter() - started)
    except (TimeoutError, OSError, ValueError):
        return CheckResult(name, False, "unavailable", perf_counter() - started)


async def run_readiness_checks(settings: Settings) -> list[CheckResult]:
    checks: list[Awaitable[CheckResult]] = [
        check_temp_directory(settings.disk_check_path),
        check_disk_space(settings.disk_check_path, settings.min_free_disk_mb),
    ]
    if settings.postgres_enabled and settings.postgres_url:
        checks.append(
            check_tcp_dependency(
                "postgresql",
                settings.postgres_url,
                settings.dependency_timeout_seconds,
                5432,
            )
        )
    if settings.redis_enabled and settings.redis_url:
        checks.append(
            check_tcp_dependency(
                "redis", settings.redis_url, settings.dependency_timeout_seconds, 6379
            )
        )
    return list(await asyncio.gather(*checks))
