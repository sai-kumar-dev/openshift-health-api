# Contributing

Use Python 3.11+, create a virtual environment, and run:

```bash
python -m pip install -e ".[dev]"
make check
```

Open an issue for behavior or architecture changes. Keep pull requests focused,
add meaningful failure-path tests, update documentation, and use conventional
commit subjects such as `feat:`, `fix:`, `test:`, or `docs:`. Do not commit
secrets, `.env` files, caches, generated coverage, or local cluster data.

Good first issues are documentation corrections and additional pure unit tests.
Protocol-level dependency checks, OpenTelemetry, and cluster deployment work
require broader context and are not beginner issues. Releases use Semantic
Versioning: behavior-compatible features increment the minor version; breaking
API/configuration changes increment the major version.
