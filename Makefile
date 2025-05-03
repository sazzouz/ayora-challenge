.PHONY: help docker-shell poetry python django admin startapp dev check migrate shell setup flush refresh docker-up docker-down docker-wipe docker-build docker-rebuild-app bootstrap test test-verbose test-parallel test-cov test-cov-html deps-update deps-export schema lint lint-fix format pre-commit

# Colors for help message
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)
TARGET_MAX_CHAR_NUM=20

## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

# Docker commands
## Enter docker shell
docker-shell:
	docker exec -it ayora /bin/bash

## Run poetry command in docker
poetry:
	docker exec -it ayora poetry $(cmd)

## Run python command through poetry in docker
python:
	docker exec -it ayora poetry run python $(cmd)

# Django commands
## Run Django admin command
admin:
	docker exec -it ayora poetry run django-admin $(cmd)

## Create new Django app
startapp:
	cd ayora && python manage.py startapp $(name)

## Run Django management command
django:
	docker exec -it ayora poetry run ./ayora/manage.py $(cmd)

## Run Django development server
dev:
	$(MAKE) django cmd="runserver"

## Run Django system checks
check:
	$(MAKE) django cmd="check"
	$(MAKE) django cmd="check --deploy"

## Run Django migrations
migrate:
	$(MAKE) django cmd="makemigrations"
	$(MAKE) django cmd="migrate"

## Enter Django shell_plus
shell:
	$(MAKE) django cmd="shell_plus --bpython"

## Run Django setup
setup:
	$(MAKE) django cmd="setup"

## Flush Django database
flush:
	$(MAKE) django cmd="flush --noinput"

## Refresh development environment
refresh: flush
	$(MAKE) django cmd="populate"
	$(MAKE) setup

# Docker compose commands
## Start docker containers
docker-up:
	docker compose up

## Stop and remove docker containers
docker-down:
	docker compose down -v --remove-orphans

## Wipe docker system
docker-wipe: docker-down
	docker system prune --all --volumes --force

## Build docker containers
docker-build: docker-down
	docker compose build
	$(MAKE) docker-up

## Rebuild specific services
docker-rebuild-app:
	docker compose build ayora celery celery-beat flower
	docker-compose up -d --no-deps --force-recreate ayora celery celery-beat flower

## Bootstrap development environment
bootstrap: pre-commit docker-build

# Testing commands
## Run tests
test:
	docker exec -it ayora poetry run pytest ./ayora/ --reuse-db $(args)

## Run verbose tests
test-verbose:
	$(MAKE) test args="-v"

## Run parallel tests
test-parallel:
	$(MAKE) test args="-n auto"

## Run tests with coverage
test-cov:
	$(MAKE) test args="--cov=ayora"

## Run tests with HTML coverage report
test-cov-html:
	$(MAKE) test args="--cov=ayora --cov-report=html"

# Dependency management
## Update dependencies
deps-update:
	docker exec -it ayora poetry update

## Export dependencies to requirements.txt
deps-export:
	docker exec -it ayora poetry export --without-hashes --format=requirements.txt > ./requirements.txt

# Documentation and code quality
## Generate API schema
schema:
	$(MAKE) django cmd="spectacular --color --file ./schema.yaml"

## Run linting
lint:
	docker exec -it ayora poetry run ruff check $(args)

## Fix linting issues
lint-fix:
	$(MAKE) lint args="--fix"

## Format code
format:
	docker exec -it ayora poetry run ruff format

## Setup pre-commit hooks
pre-commit:
	pip3 install pre-commit
	pre-commit install
	pre-commit install --hook-type commit-msg
	pre-commit autoupdate