# Observability

Logs are one JSON object per application request and lifecycle event. Request
events include UTC timestamp, level, logger, event, request ID, method, route
template, status, and duration. Uvicorn access logs are disabled in the
container to avoid duplicate records.

Prometheus families include `service_info`, `http_requests_total`,
`http_request_duration_seconds`, `readiness_status`,
`readiness_check_duration_seconds`, and `readiness_check_failures_total`.
Labels are limited to method, route template, status class, and known check name.
Metrics reset with each process restart.
