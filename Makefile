PYTHON ?= python
IMAGE ?= openshift-health-api:0.3.0

.PHONY: install run format format-check lint typecheck test coverage security manifests \
	container-build container-test smoke check ci clean

install:
	$(PYTHON) -m pip install -e ".[dev]"

run:
	$(PYTHON) -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --no-access-log --log-config app/uvicorn-logging.json

format:
	$(PYTHON) -m ruff format .

format-check:
	$(PYTHON) -m ruff format --check .

lint:
	$(PYTHON) -m ruff check .

typecheck:
	$(PYTHON) -m mypy app tests

test:
	$(PYTHON) -m pytest

coverage: test

security:
	$(PYTHON) -m pip_audit -r requirements.txt

manifests:
	kubectl kustomize deploy/overlays/development > /dev/null
	kubectl kustomize deploy/overlays/production > /dev/null

container-build:
	docker build -t $(IMAGE) -f Containerfile .

container-test:
	bash scripts/container-test.sh $(IMAGE)

smoke:
	$(PYTHON) scripts/smoke.py

check: format-check lint typecheck test

ci: check security manifests

clean:
	$(PYTHON) -c "import shutil; [shutil.rmtree(p, ignore_errors=True) for p in ('.pytest_cache','.pytest-tmp','.ruff_cache','.mypy_cache','htmlcov','build','dist')]"
