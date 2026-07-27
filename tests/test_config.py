import logging

import pytest

from app.config import ConfigurationError, Settings


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("MIN_FREE_DISK_MB", "-1"),
        ("MIN_FREE_DISK_MB", "many"),
        ("DEPENDENCY_TIMEOUT_SECONDS", "0"),
        ("DEPENDENCY_TIMEOUT_SECONDS", "slow"),
        ("LOG_LEVEL", "LOUD"),
        ("METRICS_ENABLED", "perhaps"),
    ],
)
def test_invalid_configuration_fails(name: str, value: str) -> None:
    with pytest.raises(ConfigurationError):
        Settings.from_env({name: value})


def test_optional_dependency_requires_valid_url() -> None:
    with pytest.raises(ConfigurationError, match="POSTGRES_URL"):
        Settings.from_env({"POSTGRES_CHECK_ENABLED": "true"})
    with pytest.raises(ConfigurationError, match="REDIS_URL"):
        Settings.from_env({"REDIS_CHECK_ENABLED": "true", "REDIS_URL": "http://secret@host"})


def test_valid_configuration() -> None:
    settings = Settings.from_env(
        {
            "LOG_LEVEL": "DEBUG",
            "POSTGRES_CHECK_ENABLED": "yes",
            "POSTGRES_URL": "postgresql://user:password@database:5432/app",
            "REDIS_CHECK_ENABLED": "1",
            "REDIS_URL": "rediss://:password@cache:6380/0",
        }
    )
    assert settings.log_level == logging.DEBUG
    assert settings.postgres_enabled and settings.redis_enabled
