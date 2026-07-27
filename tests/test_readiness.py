from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.checks import CheckResult


def test_readiness_failure_returns_503_without_detail_leak(client: TestClient) -> None:
    result = CheckResult("postgresql", False, "unavailable", 0.01)
    with patch("app.main.run_readiness_checks", AsyncMock(return_value=[result])):
        response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    metrics = client.get("/metrics").text
    assert "readiness_status 0.0" in metrics
    assert 'readiness_check_failures_total{check="postgresql"} 1.0' in metrics
