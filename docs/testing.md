# Testing

Unit tests mock filesystem and socket failures; integration tests recreate the
FastAPI app with isolated settings and metrics. The default suite has no network,
database, Redis, container, or cluster dependency. Branch coverage must remain at
least 90%.

`make check` is the fast gate. `make security` needs vulnerability data,
`make manifests` needs kubectl, and `scripts/container-test.sh` needs a running
Docker daemon plus Bash. Do not interpret client-side rendering as cluster
validation.
