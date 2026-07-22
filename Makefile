.PHONY: setup-backend install-backend test-backend test-backend-unit test-backend-integration lint-backend openapi-check test-api-docs setup-frontend test-frontend build-frontend db-up db-down db-logs db-migrate db-upgrade db-downgrade db-current db-seed test-db-prepare validate

setup-backend:
	python3 -m venv .venv
	.venv/bin/python -m pip install --editable 'backend[dev]'

install-backend:
	.venv/bin/python -m pip install --editable 'backend[dev]'

test-backend:
	.venv/bin/python -m pytest backend --cov=auth_test_ai --cov-report=term-missing

test-backend-unit:
	.venv/bin/python -m pytest backend/tests/unit -m unit

test-backend-integration:
	.venv/bin/python -m pytest backend/tests/integration -m integration

lint-backend:
	.venv/bin/python -m ruff check backend

openapi-check:
	.venv/bin/python scripts/validate_openapi.py

test-api-docs:
	.venv/bin/python -m pytest backend/tests/unit/test_api_docs.py -m unit

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

db-migrate:
	cd backend && AUTH_TEST_AI_ENV=$${AUTH_TEST_AI_ENV:?set AUTH_TEST_AI_ENV} ../.venv/bin/flask --app auth_test_ai:create_app db migrate

db-upgrade:
	cd backend && AUTH_TEST_AI_ENV=$${AUTH_TEST_AI_ENV:?set AUTH_TEST_AI_ENV} ../.venv/bin/flask --app auth_test_ai:create_app db upgrade

db-downgrade:
	cd backend && AUTH_TEST_AI_ENV=$${AUTH_TEST_AI_ENV:?set AUTH_TEST_AI_ENV} ../.venv/bin/flask --app auth_test_ai:create_app db downgrade -- -1

db-current:
	cd backend && AUTH_TEST_AI_ENV=$${AUTH_TEST_AI_ENV:?set AUTH_TEST_AI_ENV} ../.venv/bin/flask --app auth_test_ai:create_app db current

db-seed:
	cd backend && AUTH_TEST_AI_ENV=development ALLOW_DEV_SEED=true ../.venv/bin/flask --app auth_test_ai:create_app seed-dev-users

test-db-prepare:
	docker compose exec -T postgres sh -c 'if psql -U "$$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '\''auth_test_ai_test'\''" | grep -q 1; then exit 0; else createdb -U "$$POSTGRES_USER" auth_test_ai_test; fi'

validate: lint-backend test-backend test-frontend build-frontend
