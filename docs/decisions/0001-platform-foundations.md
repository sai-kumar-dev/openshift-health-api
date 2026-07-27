# ADR 0001: Platform foundations

Status: accepted, 2026-07-27.

Use FastAPI for typed OpenAPI-capable endpoints; Red Hat UBI 9 Python for
OpenShift alignment; Kustomize for low-duplication overlays; and
`prometheus-client` for standards-compliant exposition. Separate liveness from
readiness so downstream failure cannot trigger restart loops. Disable optional
dependencies by default so local operation is deterministic. Support arbitrary
UIDs because OpenShift assigns identities at runtime.

Consequences are an additional small metrics dependency, OpenShift-specific
Route resources, and explicit overlay patches. These costs are preferable to
hand-written metric encoding, duplicated YAML, or fixed-UID assumptions.
