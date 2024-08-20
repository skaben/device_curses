.DEFAULT_GOAL := help

ACCENT = $(shell tput setaf 4)
RESET := $(shell tput sgr0)

APP := skaben_device

.PHONY: install-hooks
install-hooks:  ## Установить хуки pre-commit
	@python3 -m pip install pre-commit
	@pre-commit install

.PHONY: build
build:  ## Собрать контейнер для линтера и тестов
	@docker-compose build --no-cache

.PHONY: test
test:  ## Запустить тесты
	@docker-compose run --rm ${APP} sh -c pytest tests

.PHONY: lint-fix
lint:  ## Запустить линтер для авто-форматирования
	@docker-compose run --rm ${APP} ruff check --no-cache . && ruff format --no-cache .

.PHONY: help
help:
	@echo
	@grep -E '^[a-zA-Z.%_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?## "}; {printf "%2s$(ACCENT)%-15s${RESET} %s\n", " ", $$1, $$2}'
	@echo
