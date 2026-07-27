# Interview guide

I built OpenShift Health API to show the difference between a process being
alive and being safe to receive traffic. Liveness never depends on downstream
systems, while readiness runs optional PostgreSQL and Redis reachability checks
concurrently with strict timeouts, so an outage does not cause restart storms or
a hanging probe. The API sanitizes request IDs, returns safe problem details,
emits structured JSON logs, and keeps Prometheus labels bounded.

The service runs on a minimal Red Hat UBI image as a non-root arbitrary UID with
a read-only root filesystem and only `/tmp` writable. Kustomize overlays add
probes, resource controls, autoscaling, disruption protection, topology spread,
and NetworkPolicy. Twenty-seven deterministic tests provide 96.07% branch-aware
coverage, with strict mypy and Ruff checks. GitHub Actions has passed the Python
matrix, dependency and secret audits, manifest validation, container smoke test,
and Trivy scans. I have not claimed an OpenShift deployment because no cluster
context or published Quay image was available. My next improvement would be a
protocol-level dependency check followed by a real OpenShift rollout.
