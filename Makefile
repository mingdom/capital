VENV=venv
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
BLACK=$(VENV)/bin/black
RUFF=$(VENV)/bin/ruff
PYTEST=$(VENV)/bin/pytest

.PHONY: dev install format lint test run run-benchmarks report clean hook

$(PY):
	python3 -m venv $(VENV)

install: $(PY)
	$(PIP) install -U pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r dev-requirements.txt

dev: install

format: $(BLACK)
	$(BLACK) .

$(BLACK): install ; @true

lint: $(RUFF)
	$(RUFF) check .

$(RUFF): install ; @true

test: $(PYTEST)
	PYTHONPATH=. $(PYTEST) -q

$(PYTEST): install ; @true

run: $(PY)
	$(PY) sortino.py

run-benchmarks: $(PY)
	$(PY) sortino.py --benchmarks

report: $(PY)
	$(PY) scripts/build_report.py

clean:
	rm -rf $(VENV) __pycache__ .pytest_cache .coverage htmlcov

hook:
	chmod +x scripts/pre-commit.sh
	ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit
	@echo "Installed Git pre-commit hook."
