SHELL := /bin/bash

COMPOSE ?= docker compose
COMPOSE_FILE ?= docker-compose.yaml
ENV_FILE ?= .env.example
API_SERVICE ?= productory-demo
DB_SERVICE ?= productory-db
SERVICE ?= $(API_SERVICE)
TEST ?=

DC := $(COMPOSE) --env-file $(ENV_FILE) -f $(COMPOSE_FILE)

.DEFAULT_GOAL := help

.PHONY: help install-dev qa coverage demo-migrate demo-run demo-stop demo-logs demo-check up down restart logs ps migrations superuser drop-create-db loaddata show-urls test test-quick test-one test-all shell ipython

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*##' Makefile | sort | awk 'BEGIN {FS = ":.*## "}; {printf "%-18s %s\n", $$1, $$2}'

install-dev: ## Install package + dev dependencies locally
	python3 -m pip install -e '.[dev]'

qa: ## Run lint, format check, type check, and tests
	python3 -m ruff check src tests demo
	python3 -m ruff format --check src tests demo --exclude '*/migrations/*'
	python3 -m mypy src
	python3 -m pytest tests

coverage: ## Run tests with coverage report
	python3 -m coverage run -m pytest tests
	python3 -m coverage report

demo-migrate: ## Run migrations for the demo project
	$(DC) up -d $(DB_SERVICE) $(API_SERVICE)
	$(DC) exec $(API_SERVICE) python demo/manage.py migrate

demo-run: ## Run demo stack in detached docker mode
	$(DC) up -d --build $(DB_SERVICE) $(API_SERVICE)
	$(DC) exec $(API_SERVICE) python demo/manage.py migrate
	$(DC) exec $(API_SERVICE) python demo/manage.py seed_demo_data --reset

demo-stop: ## Stop detached demo docker stack
	$(DC) down

demo-logs: ## Tail demo container logs
	$(DC) logs -f --tail=200 $(API_SERVICE)

demo-check: ## Run Django checks for demo project
	python3 demo/manage.py check

up: ## Start and build docker services
	$(DC) up -d --build

down: ## Stop and remove docker services
	$(DC) down --remove-orphans

restart: ## Restart services (override with SERVICE=<name>)
	$(DC) restart $(SERVICE)

logs: ## Tail logs (override with SERVICE=<name>)
	$(DC) logs -f --tail=200 $(SERVICE)

ps: ## List running services
	$(DC) ps

migrations: ## Create and apply Django migrations in docker
	$(DC) exec $(API_SERVICE) python demo/manage.py makemigrations
	$(DC) exec $(API_SERVICE) python demo/manage.py migrate

superuser: ## Create a Django superuser in docker
	$(DC) exec $(API_SERVICE) python demo/manage.py createsuperuser

drop-create-db: ## Nuke Postgres DB (DROP + CREATE) and re-run migrations
	$(DC) up -d $(DB_SERVICE) $(API_SERVICE)
	$(DC) exec -T $(DB_SERVICE) sh -lc 'psql -U "$$POSTGRES_USER" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='\''$$POSTGRES_DB'\'' AND pid <> pg_backend_pid();" -c "DROP DATABASE IF EXISTS \"$$POSTGRES_DB\";" -c "CREATE DATABASE \"$$POSTGRES_DB\";"'
	$(DC) exec $(API_SERVICE) python demo/manage.py migrate

loaddata: ## Seed dynamic demo data in docker (50 products, bundles, promotions)
	$(DC) exec $(API_SERVICE) python demo/manage.py seed_demo_data --reset

show-urls: ## Print resolved Django URL patterns in docker
	$(DC) exec -T $(API_SERVICE) python demo/manage.py shell -c "from django.urls import URLPattern, get_resolver; \
	def walk(patterns, prefix=''): \
	    [print(prefix + str(p.pattern)) if isinstance(p, URLPattern) else walk(p.url_patterns, prefix + str(p.pattern)) for p in patterns]; \
	walk(get_resolver().url_patterns)"

test: test-quick ## Run quick tests in docker

test-quick: ## Run quick smoke tests in docker (fail fast)
	$(DC) exec $(API_SERVICE) python -m pytest tests/test_services.py tests/test_api.py --maxfail=1 -q

test-one: ## Run one test in docker (pass TEST=tests/test_api.py::test_x)
	@if [ -z "$(strip $(TEST))" ]; then \
		echo "Usage: make test-one TEST=tests/test_api.py::test_catalog_and_checkout_flow"; \
		exit 1; \
	fi
	$(DC) exec $(API_SERVICE) python -m pytest $(TEST) -q

test-all: ## Run full test suite in docker
	$(DC) exec $(API_SERVICE) python -m pytest tests -q

shell: ## Open Django shell in docker
	$(DC) exec $(API_SERVICE) python demo/manage.py shell

ipython: ## Open Django shell with IPython in docker if available
	$(DC) exec $(API_SERVICE) sh -lc 'python demo/manage.py shell -i ipython || python demo/manage.py shell'
