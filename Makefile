.PHONY: help install install-dev test test-cov lint format clean build upload docs

help:
	@echo "LazzyORM Development Commands"
	@echo "=============================="
	@echo "install        - Install package"
	@echo "install-dev    - Install package with dev dependencies"
	@echo "test           - Run tests"
	@echo "test-cov       - Run tests with coverage report"
	@echo "lint           - Run linting (flake8)"
	@echo "format         - Format code (black & isort)"
	@echo "type-check     - Run type checking (mypy)"
	@echo "clean          - Clean build artifacts"
	@echo "build          - Build distribution packages"
	@echo "upload         - Upload to PyPI"
	@echo "upload-test    - Upload to Test PyPI"
	@echo "docs           - Build documentation"

install:
	pip install -e .

install-dev:
	pip install -e .[dev]

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=lazzy_orm --cov-report=html --cov-report=term-missing

lint:
	flake8 lazzy_orm/ --max-line-length=120 --exclude=__pycache__

format:
	black lazzy_orm/ tests/ --line-length=120
	isort lazzy_orm/ tests/ --profile=black

type-check:
	mypy lazzy_orm/ --ignore-missing-imports

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

upload: build
	twine upload dist/*

upload-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

docs:
	cd docs && mkdocs build
