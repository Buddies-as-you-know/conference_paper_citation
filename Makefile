.PHONY: dev run test fix ruff-fix black \
       lint ruff-check black-check mypy

dev:
	poetry run uvicorn backend.main:app --reload

build:
	docker build -t myapp .

run:
	docker build -t myapp .
	docker run -p 8000:8000 myapp

test:
	poetry run pytest

fix: ruff-fix black

ruff-fix:
	poetry run ruff --fix .

black:
	poetry run black .

lint: black-check ruff-check mypy hadolint

ruff-check:
	poetry run ruff check .

black-check:
	poetry run black --check .

mypy:
	poetry run mypy . --config-file ./pyproject.toml

hadolint:
	hadolint Dockerfile

