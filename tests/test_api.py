import json
import logging
import re

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import VERSION
from app.observability import JsonFormatter


def test_liveness_and_openapi(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "openshift-health-api",
        "version": VERSION,
    }
    assert response.headers["x-content-type-options"] == "nosniff"
    document = client.get("/openapi.json").json()
    assert document["info"]["title"] == "OpenShift-Ready Service Health API"
    assert document["info"]["version"] == VERSION


def test_readiness_reports_safe_checks(client: TestClient) -> None:
    response = client.get("/readyz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert {item["name"] for item in payload["checks"]} == {"temp_directory", "disk_space"}
    assert all(item["detail"] in {"writable", "sufficient"} for item in payload["checks"])


def test_system_endpoint_is_safe(client: TestClient) -> None:
    payload = client.get("/api/v1/system?secret=hidden").json()
    assert payload["service"] == "openshift-health-api"
    assert payload["uptime_seconds"] >= 0
    assert {"python", "architecture", "platform"} <= payload.keys()
    assert "secret" not in str(payload)


def test_metrics_use_bounded_route_labels(client: TestClient) -> None:
    client.get("/does-not-exist/one")
    client.get("/does-not-exist/two")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain; version=")
    assert "http_requests_total" in response.text
    assert 'route="unmatched"' in response.text
    assert "does-not-exist" not in response.text
    assert "service_info" in response.text


def test_request_id_generated_preserved_and_sanitized(client: TestClient) -> None:
    generated = client.get("/healthz").headers["x-request-id"]
    assert re.fullmatch(r"[0-9a-f-]{36}", generated)
    assert (
        client.get("/healthz", headers={"X-Request-ID": "demo-42"}).headers["x-request-id"]
        == "demo-42"
    )
    malicious = client.get("/healthz", headers={"X-Request-ID": "bad\nvalue"}).headers[
        "x-request-id"
    ]
    assert malicious != "bad\nvalue"
    assert (
        client.get("/healthz", headers={"X-Request-ID": "x" * 129}).headers["x-request-id"]
        != "x" * 129
    )


def test_unknown_route_has_consistent_problem(client: TestClient) -> None:
    response = client.get("/missing")
    body = response.json()
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert body["status"] == 404
    assert body["request_id"] == response.headers["x-request-id"]


def test_unhandled_error_is_safe(settings) -> None:  # type: ignore[no-untyped-def]
    app: FastAPI = __import__("app.main", fromlist=["create_app"]).create_app(settings)

    @app.get("/explode")
    async def explode() -> None:
        raise RuntimeError("sensitive internal detail")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/explode")
    assert response.status_code == 500
    assert "sensitive" not in response.text
    assert response.json()["request_id"] == response.headers["x-request-id"]


def test_request_log_is_valid_json() -> None:
    log_record = logging.LogRecord("service", logging.INFO, "", 0, "request_completed", (), None)
    log_record.request_id = "logged-1"
    log_record.route = "/healthz"
    log_record.status_code = 200
    record = json.loads(JsonFormatter().format(log_record))
    assert record["request_id"] == "logged-1"
    assert record["route"] == "/healthz"
    assert record["status_code"] == 200
