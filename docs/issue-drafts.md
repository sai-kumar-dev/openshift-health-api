# Issue drafts

These are local drafts, not published GitHub issues.

1. **Implement protocol-level PostgreSQL readiness** — replace TCP reachability
   with a lightweight authenticated `SELECT 1`, retain strict timeout/redaction,
   and mock every outcome. Not a good first issue.
2. **Implement Redis PING readiness** — support TLS and authentication without
   leaking addresses or errors. Not a good first issue.
3. **Add optional ServiceMonitor overlay** — provide a separate overlay and
   document the Prometheus Operator CRD validation boundary.
4. **Document OpenShift Local exercise** — add reproducible CRC prerequisites,
   commands, cleanup, and honest evidence. Good first issue for a contributor
   already familiar with CRC.
5. **Add opt-in OpenTelemetry tracing** — disabled by default, bounded attributes,
   and no collector requirement in basic tests. Not a good first issue.
6. **Clarify Windows setup troubleshooting** — test PowerShell commands and
   document common virtual-environment issues. Good first issue.
