PYTHON ?= python3
RUFF ?= ruff

.PHONY: help build test lint check

help:
	@printf 'build  Compile ESP32 firmware with an exported ESP-IDF environment\n'
	@printf 'test   Run Flask API tests with temporary SQLite storage\n'
	@printf 'lint   Check Python formatting and static errors\n'
	@printf 'check  Run Python syntax, lint, and server tests\n'

build:
	idf.py build

test:
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(RUFF) check server tests
	$(RUFF) format --check server tests

check: lint
	$(PYTHON) -m compileall -q server tests
	$(MAKE) test PYTHON=$(PYTHON)
