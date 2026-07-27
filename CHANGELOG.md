# Changelog

This project follows Semantic Versioning.

## 0.3.0 - 2026-07-27

- Add validated centralized configuration and safe problem responses.
- Add concurrent optional PostgreSQL and Redis reachability checks.
- Add bounded Prometheus request and readiness metrics.
- Harden JSON logging, request IDs, container, and OpenShift manifests.
- Add branch coverage, strict mypy, security auditing, Kustomize overlays, and expanded tests.
- Update FastAPI and Starlette to versions that resolve the hosted dependency audit.
- Use a minimal UBI 9.8 runtime and remove unused curl packages from the final image.
- Update pytest to 9.0.3 to resolve GitHub's development-dependency alert.
- Move the core GitHub Actions integrations to their Node 24 generations and
  authenticate Gitleaks on pull-request events with the workflow token.
- Update pytest to 9.1.1 and Ruff to 0.16.0 after full quality-suite validation,
  and apply the FastAPI 0.140.4 patch update.
- Replace the stale README run snapshot with the durable CI workflow link and
  refresh the dated hosted-validation evidence.

## 0.2.0

- Initial health, readiness, diagnostics, metrics, container, and OpenShift MVP.
