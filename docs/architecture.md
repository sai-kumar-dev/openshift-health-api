# Architecture

`create_app()` owns immutable settings, logging, metrics, and lifespan state.
Middleware establishes a safe request ID, normalizes unexpected failures, emits
bounded metrics, and writes one access event. Platform routes delegate readiness
to small async check functions.

```mermaid
flowchart LR
  C[Client] --> M[Request middleware]
  M --> R[Routes]
  R --> H[Liveness]
  R --> Q[Concurrent readiness]
  Q --> T[Temp and disk]
  Q --> D[Optional dependency sockets]
  M --> O[JSON logs and metrics]
```

This deliberately avoids a repository/service hierarchy: four small modules
provide enough separation for this service size.
