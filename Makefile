PYTHON ?= python3
ARGS ?=

.PHONY: run test lint

run:
	$(PYTHON) -m src.main $(ARGS)

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m flake8 --max-line-length=79 src tests
