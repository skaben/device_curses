.DEFAULT_GOAL := help

ACCENT = $(shell tput setaf 4)
RESET := $(shell tput sgr0)

APP := skaben_device

.PHONY: build
build:  ## Собрать контейнер для линтера и тестов
	@docker-compose build --no-cache

.PHONY: test
test:  ## Запустить тесты
	@docker-compose run --rm ${APP} sh -c pytest tests

.PHONY: lint
lint:  ## Запустить линтер
	@docker-compose run --rm ${APP} ./run-lint.sh

.PHONY: help
help:
	@echo
	@grep -E '^[a-zA-Z.%_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?## "}; {printf "%2s$(ACCENT)%-15s${RESET} %s\n", " ", $$1, $$2}'
	@echo