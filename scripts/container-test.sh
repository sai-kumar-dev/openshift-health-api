#!/usr/bin/env bash
set -euo pipefail
image="${1:-openshift-health-api:0.3.0}"
name="openshift-health-api-test-$$"
trap 'docker rm -f "$name" >/dev/null 2>&1 || true' EXIT
docker run -d --name "$name" --user 1000710000:0 --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=64m -p 18080:8080 "$image" >/dev/null
for _ in $(seq 1 30); do
  if BASE_URL=http://127.0.0.1:18080 python scripts/smoke.py; then exit 0; fi
  sleep 1
done
docker logs "$name"
exit 1
