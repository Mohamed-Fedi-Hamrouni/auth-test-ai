.PHONY: setup-backend test-backend lint-backend setup-frontend test-frontend build-frontend db-up db-down db-logs validate

setup-backend:
	python3 -m venv .venv
	.venv/bin/python -m pip install --editable 'backend[dev]'

test-backend:
	.venv/bin/python -m pytest backend

lint-backend:
	.venv/bin/python -m ruff check backend

setup-frontend:
	npm --prefix frontend install

test-frontend:
	npm --prefix frontend test -- --watch=false

build-frontend:
	npm --prefix frontend run build

db-up:
	docker compose up --detach postgres

db-down:
	docker compose down

db-logs:
	docker compose logs --follow postgres

validate: lint-backend test-backend test-frontend build-frontend
