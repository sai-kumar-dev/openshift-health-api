"""Dependency-free HTTP smoke test for a running service."""

from __future__ import annotations

import json
import os
from urllib.request import urlopen

base_url = os.getenv("BASE_URL", "http://127.0.0.1:8080")
for endpoint in ("/healthz", "/readyz", "/api/v1/system", "/metrics"):
    with urlopen(f"{base_url}{endpoint}", timeout=3) as response:  # noqa: S310
        if response.status != 200:
            raise SystemExit(f"{endpoint}: HTTP {response.status}")
        if endpoint != "/metrics":
            json.loads(response.read())
print("smoke: all endpoints returned HTTP 200")
