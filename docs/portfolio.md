# Portfolio copy

## GitHub description

Production-minded FastAPI health service with Red Hat UBI, OpenShift security
controls, Prometheus metrics, structured logging, Kustomize overlays, and
comprehensive testing.

## Portfolio summary

OpenShift Health API is a compact platform-engineering project that demonstrates
how orchestrators distinguish process liveness from traffic readiness. It
combines validated configuration, timeout-isolated dependency checks, structured
JSON logs, and bounded Prometheus metrics with a Red Hat UBI container designed
for arbitrary non-root UIDs and a read-only root filesystem. Deterministic tests
enforce branch coverage and strict typing, while Kustomize overlays model
development and production deployment controls. The public GitHub repository has
passing hosted validation for Python 3.11–3.13, dependency and secret audits,
manifest checks, a strict container smoke test, and Trivy scans. The container is
locally validated; Quay publication and a real OpenShift rollout remain
documented external steps.
