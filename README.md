# OpenShift-Ready Service Health API

[![CI](https://github.com/sai-kumar-dev/openshift-health-api/actions/workflows/ci.yml/badge.svg)](https://github.com/sai-kumar-dev/openshift-health-api/actions/workflows/ci.yml)

A compact FastAPI portfolio service that demonstrates production-minded health
semantics, observability, secure container defaults, and maintainable OpenShift
deployment without pretending to be a complete enterprise platform.

## What it demonstrates

- `/healthz` process liveness, independent of downstream services
- `/readyz` concurrent, timeout-bounded temp, disk, PostgreSQL, and Redis checks
- safe diagnostics, RFC 7807-style errors, sanitized request IDs, JSON logs
- Prometheus request/readiness metrics with bounded labels
- Red Hat UBI 9 Python, non-root and arbitrary-UID operation, read-only root support
- Kustomize development and production overlays with restricted pod security
- Ruff, strict mypy, deterministic tests, branch coverage, and dependency auditing

## Architecture

```text
client -> request/error middleware -> platform and diagnostics routes
                    |                  |-> concurrent readiness checks
                    |                  `-> isolated Prometheus registry
                    `-> one structured access log
OpenShift Route -> Service -> hardened Deployment -> /tmp emptyDir
```

Configuration is read and validated once while the application is created.
Independent readiness checks run concurrently; optional network checks are off by
default and expose only `reachable` or `unavailable`.

## Endpoints

| Endpoint | Purpose | Success |
|---|---|---|
| `GET /healthz` | Process liveness | 200 |
| `GET /readyz` | Traffic eligibility | 200, or 503 if a check fails |
| `GET /api/v1/system` | Non-sensitive runtime metadata | 200 |
| `GET /metrics` | Prometheus exposition | 200 |
| `GET /docs`, `/openapi.json` | Development API documentation | 200 |

## Local development

Python 3.11 or later is required.

```bash
python -m venv .venv
source .venv/bin/activate  # PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
make check
make run
```

Direct Windows equivalents use `python -m ruff`, `python -m mypy`, and
`python -m pytest`. `make ci` also needs `kubectl` and internet access for the
vulnerability database.

## Configuration

| Variable | Default | Constraint |
|---|---:|---|
| `SERVICE_NAME` | `openshift-health-api` | display/metric metadata |
| `SERVICE_VERSION` | package version | deployment override |
| `LOG_LEVEL` | `INFO` | standard Python level |
| `MIN_FREE_DISK_MB` | `64` | 0–1,048,576 |
| `DISK_CHECK_PATH` | OS temp directory | writable runtime path |
| `DEPENDENCY_TIMEOUT_SECONDS` | `1` | 0.05–30 |
| `POSTGRES_CHECK_ENABLED` | `false` | boolean |
| `POSTGRES_URL` | unset | `postgres://` or `postgresql://`; required if enabled |
| `REDIS_CHECK_ENABLED` | `false` | boolean |
| `REDIS_URL` | unset | `redis://` or `rediss://`; required if enabled |
| `METRICS_ENABLED` | `true` | boolean |

Dependency URLs may contain credentials but are never returned or logged. The
checks verify bounded TCP reachability, not authentication or query correctness;
that is an intentional MVP trade-off.

## Quality and security commands

```bash
make format-check  # formatting
make lint          # Ruff rules
make typecheck     # strict mypy
make test          # tests, branch coverage, 90% threshold
make security      # pip-audit runtime dependencies
make check         # fast checks
make ci            # check + audit + Kustomize rendering
```

## Container

`Containerfile` is the single canonical definition.

```bash
docker build --build-arg VCS_REF="$(git rev-parse --short HEAD)" \
  -t openshift-health-api:0.3.0 -f Containerfile .
docker run --rm -p 8080:8080 openshift-health-api:0.3.0
bash scripts/container-test.sh openshift-health-api:0.3.0
```

The integration script uses a random OpenShift-style UID, a read-only root
filesystem, and a restricted `/tmp` tmpfs before smoke-testing all endpoints.
Uvicorn runs directly because this stateless MVP scales with pod replicas and
needs no in-container process manager.

## OpenShift

Render before applying:

```bash
kubectl kustomize deploy/overlays/development
kubectl kustomize deploy/overlays/production
oc apply -k deploy/overlays/development
```

Create the namespace and publish an image first. Replace `REGISTRY_NAMESPACE` in
the production overlay with a real registry organization and prefer an image digest
for an actual production release. The production overlay adds three replicas,
an HPA, PDB, and topology spread. The ingress-only NetworkPolicy intentionally
does not restrict egress so DNS and optional dependencies continue to work;
tighten it against known namespace selectors in a real environment.

## Observability and security

Each request produces one UTC JSON event containing method, route template,
status, duration, and safe request ID. Query strings, headers, bodies, exception
messages, dependency addresses, and credentials are excluded. Metric labels use
route templates or `unmatched`, never raw paths. See
[observability](docs/observability.md) and the [threat model](docs/security.md).

## Decisions and trade-offs

- Optional dependencies do not affect liveness and are disabled by default.
- Per-app Prometheus registries prevent duplicate collectors in tests.
- Kustomize keeps environment differences visible without introducing Helm.
- A single Uvicorn process favors Kubernetes horizontal scaling and clear signals.
- OpenAPI remains enabled for portfolio usability; production operators may gate it.

## Verification status

| Validation | Status | Evidence |
|---|---|---|
| Ruff formatting and lint | Verified locally | `ruff format --check .`; `ruff check .` |
| Strict mypy | Verified locally | `python -m mypy app tests` |
| Tests and branch coverage | Verified locally | `python -m pytest`; see [release validation](docs/validation/0.3.0.md) |
| Kustomize overlays | Verified locally | Development and production rendered client-side |
| Dependency audit | Verified in hosted CI | `pip-audit` passed for runtime dependencies |
| Secret scan | Verified in hosted CI | Gitleaks passed |
| Manifest scan | Verified in hosted CI | Trivy configuration scan passed |
| Container scan | Verified in hosted CI | Trivy HIGH/CRITICAL image gate passed |
| Container runtime | Verified locally and in CI | Docker; arbitrary UID and read-only-root smoke tests |
| Hosted CI | Passing | [View hosted CI runs](https://github.com/sai-kumar-dev/openshift-health-api/actions/workflows/ci.yml) |
| Kubernetes/OpenShift | Unavailable | No cluster tools or context available |

Client-side Kustomize rendering is not Kubernetes or OpenShift deployment
validation. Exact dated results and limitations are recorded in the
[0.3.0 validation record](docs/validation/0.3.0.md).

## Limitations and roadmap

The dependency checks prove connectivity rather than protocol health. There is
no authentication because all endpoints are operational metadata; exposure
should be controlled at the Route/network layer. Next valuable work is real
PostgreSQL/Redis protocol checks, ServiceMonitor packaging, OpenTelemetry as an
opt-in, SHA-pinned CI actions, and an OpenShift Local deployment exercise.

See [contributing](CONTRIBUTING.md), [deployment](docs/deployment.md),
[testing](docs/testing.md), [changelog](CHANGELOG.md), [security policy](SECURITY.md),
and the [MIT license](LICENSE).
