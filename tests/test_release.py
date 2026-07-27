"""Release metadata consistency tests."""

import json
from pathlib import Path

from app.config import VERSION

ROOT = Path(__file__).parents[1]


def test_release_version_is_consistent() -> None:
    expected_references = {
        "pyproject.toml": f'version = "{VERSION}"',
        "Containerfile": f'ARG APP_VERSION="{VERSION}"',
        "deploy/base/deployment.yaml": f"image: openshift-health-api:{VERSION}",
        "deploy/base/kustomization.yaml": f"app.kubernetes.io/version: {VERSION}",
        "deploy/overlays/production/kustomization.yaml": f"newTag: {VERSION}",
        "CHANGELOG.md": f"## {VERSION} -",
    }
    for relative_path, expected in expected_references.items():
        assert expected in (ROOT / relative_path).read_text(encoding="utf-8")


def test_only_one_registry_namespace_placeholder_exists() -> None:
    matches: list[str] = []
    for path in ROOT.rglob("*"):
        if path.is_file() and not any(
            part in {".git", ".venv", "__pycache__", "tests"} for part in path.parts
        ):
            if "REGISTRY_NAMESPACE" in path.read_text(encoding="utf-8", errors="ignore"):
                matches.append(path.relative_to(ROOT).as_posix())
    assert matches == ["README.md", "deploy/overlays/production/kustomization.yaml"]


def test_ci_build_uses_real_revision_and_source() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "--build-arg VCS_REF=${{ github.sha }}" in workflow
    assert "--build-arg SOURCE_URL=${{ github.server_url }}/${{ github.repository }}" in workflow


def test_uvicorn_logging_configuration_is_valid_json() -> None:
    config = json.loads((ROOT / "app/uvicorn-logging.json").read_text(encoding="utf-8"))
    assert config["formatters"]["json"]["()"] == "app.observability.JsonFormatter"
    assert config["loggers"]["uvicorn.access"]["propagate"] is False
