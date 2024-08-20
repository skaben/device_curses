.DEFAULT_GOAL := help

ACCENT = $(shell tput setaf 4)
RESET := $(shell tput sgr0)

APP := skaben_device

DIST ?= dist.tar.gz
VENV ?= ~/skaben-term-venv
PYTHON_VERSION := 3.10
PYTHON_PATH := ${VENV}/bin/python${PYTHON_VERSION}


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

.PHONY: install
install:  ##  создать конфиг по умолчанию
	@rm -rf conf resources
	@chmod +x pre-run.sh
	@./pre-run.sh install

.PHONY: run
run:  ##  run application
	@${PYTHON} app.py

.PHONY: clean
clean:  ##  clean application running conf
	@rm -rf ./conf
	@rm -rf ./resources

.PHONY: init
init:  clean config front  ##  полная инициализация с нуля

.PHONY: help
help:
	@echo
	@grep -E '^[a-zA-Z.%_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | awk 'BEGIN {FS = ":.*?## "}; {printf "%2s$(ACCENT)%-15s${RESET} %s\n", " ", $$1, $$2}'
	@echo
