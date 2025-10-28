.PHONY: help install install-dev build dist clean test check lint format

SRC_DIR = c_struct_parser
MAIN_SCRIPT = $(SRC_DIR)/c_struct_parser.py

help:
	@echo "Available targets:"
	@echo "  install      - Install the package in the current environment"
	@echo "  install-dev  - Install in editable mode with dev dependencies"
	@echo "  build        - Build source and wheel distributions"
	@echo "  dist         - Alias for build"
	@echo "  clean        - Remove build artifacts and cache"
	@echo "  lint         - Run all linters and type checks (via pre-commit)"
	@echo "  test         - Run basic unit test with pytest"
	@echo "  check        - Validate package metadata and structure"
	@echo "  help         - Show this help"

install:
	pip install .

install-dev:
	pip install -e .[dev]

build dist: clean
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

test:
	@echo "==> Running unit tests..."
	@if command -v pytest >/dev/null 2>&1; then \
		pytest tests/ -v --tb=short; \
	else \
		echo "pytest not found. Install with: pip install -e .[test]"; \
		exit 1; \
	fi

lint:
	@echo "==> Running linters and type checks..."
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit run --all-files; \
	else \
		echo "pre-commit not found. Install with: pip install -e .[dev]"; \
		exit 1; \
	fi

format:
	@echo "==> Formatting code with Black..."
	@if command -v black >/dev/null 2>&1; then \
		black c_struct_parser/ tests/; \
	else \
		echo "black not found. Install dev dependencies with: make install-dev"; \
		exit 1; \
	fi

check:
	@echo "==> Checking package structure..."
	@test -f pyproject.toml || (echo "pyproject.toml missing"; exit 1)
	@test -f $(MAIN_SCRIPT) || (echo "Main script missing"; exit 1)
	@test -f README.md || (echo "README.md missing"; exit 1)
	@test -f LICENSE || (echo "LICENSE missing"; exit 1)
	@test -d tests || (echo "tests/ directory missing"; exit 1)
	@echo "=> All required files present."
