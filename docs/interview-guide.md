# Interview guide

1. **What problem does it solve?** It provides operational endpoints and
   deployment conventions that let an orchestrator decide whether a process is
   alive and ready for traffic while giving operators safe logs and metrics.
2. **Why separate liveness and readiness?** They drive different actions:
   liveness may restart a process; readiness only removes it from traffic.
3. **Why no dependencies in liveness?** A database outage must not create a
   restart storm in otherwise healthy application pods.
4. **Why concurrent readiness checks?** Independent latency should overlap, so
   total time approaches the slowest check instead of the sum.
5. **Why timeouts?** A health endpoint that hangs cannot reliably protect traffic.
6. **Why transport-level dependency checks?** They demonstrate bounded failure
   isolation with no database drivers. They prove reachability, not query health;
   protocol checks are the next step when those dependencies are real.
7. **Why a Prometheus registry per app?** Tests and multiple app instances do not
   collide through process-global collectors.
8. **How are metric labels bounded?** Routes use framework templates or the
   constant `unmatched`; request IDs, raw paths, queries, and errors are excluded.
9. **How are request IDs sanitized?** A length-limited allowlist accepts safe
   identifiers. Missing or invalid values are replaced by UUIDs.
10. **Why Red Hat UBI?** It aligns runtime behavior and support conventions with
    OpenShift while remaining a familiar Python container base.
11. **How does arbitrary UID execution work?** Code is world-readable, runtime
    writes are limited to `/tmp`, and no username lookup or fixed home is required.
12. **Why group 0 permissions?** OpenShift commonly assigns an arbitrary UID
    while preserving root-group membership, allowing carefully scoped group
    access without granting root privileges. This image currently needs no
    writable application directory.
13. **Why read-only root?** It reduces persistence and tampering opportunities.
14. **Why an `emptyDir` at `/tmp`?** Readiness needs a deliberate writable area,
    and its lifecycle should follow the pod rather than the image filesystem.
15. **Why disable service-account tokens?** The service does not call the
    Kubernetes API, so mounting credentials creates needless exposure.
16. **Why Kustomize?** The environments differ by a few resources and patches;
    a full template language would add unnecessary complexity.
17. **Why one Uvicorn worker?** Kubernetes owns replication, health, and resource
    limits; one process gives clean signals and predictable pod accounting.
18. **How does the HPA interact with replicas?** Production starts and scales no
    lower than three replicas, up to six based on CPU, consistent with the PDB.
19. **What does NetworkPolicy protect?** It restricts pod ingress to port 8080.
    Egress remains open until real DNS and dependency selectors are known.
20. **What remains incomplete?** Container runtime, scans, hosted CI, and
    OpenShift rollout need external execution evidence; dependency checks are TCP-level.
21. **What next?** Add one protocol-level dependency check and validate the
    published image on OpenShift Local before adding tracing or more packaging.
