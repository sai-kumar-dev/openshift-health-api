import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.checks import check_disk_space, check_tcp_dependency, check_temp_directory


@pytest.mark.anyio
async def test_temp_failure_is_safe(tmp_path: Path) -> None:
    with patch.object(Path, "write_text", side_effect=OSError("/private/probe")):
        result = await check_temp_directory(tmp_path)
    assert not result.ok
    assert result.detail == "unavailable"


@pytest.mark.anyio
async def test_disk_failure_and_low_space(tmp_path: Path) -> None:
    with patch("app.checks.shutil.disk_usage", side_effect=OSError("secret")):
        assert not (await check_disk_space(tmp_path, 1)).ok
    with patch("app.checks.shutil.disk_usage") as usage:
        usage.return_value.free = 1024
        result = await check_disk_space(tmp_path, 1)
    assert not result.ok
    assert result.detail == "insufficient"


@pytest.mark.anyio
async def test_dependency_success() -> None:
    writer = MagicMock()
    writer.wait_closed = AsyncMock()
    with patch("app.checks.asyncio.open_connection", AsyncMock(return_value=(object(), writer))):
        result = await check_tcp_dependency("redis", "redis://secret@internal:6379", 0.1, 6379)
    assert result.ok and result.detail == "reachable"
    writer.close.assert_called_once()


@pytest.mark.anyio
@pytest.mark.parametrize("failure", [OSError("host"), TimeoutError()])
async def test_dependency_failure_is_safe(failure: Exception) -> None:
    with patch("app.checks.asyncio.open_connection", AsyncMock(side_effect=failure)):
        result = await check_tcp_dependency(
            "postgresql", "postgresql://user:secret@internal/db", 0.05, 5432
        )
    assert not result.ok
    assert result.detail == "unavailable"


@pytest.mark.anyio
async def test_dependency_timeout() -> None:
    async def never(*args, **kwargs):  # type: ignore[no-untyped-def]
        await asyncio.sleep(1)

    with patch("app.checks.asyncio.open_connection", never):
        result = await check_tcp_dependency("redis", "redis://cache", 0.001, 6379)
    assert not result.ok
