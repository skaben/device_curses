.DEFAULT_GOAL := help

ACCENT  := $(shell tput -Txterm setaf 2)
RESET := $(shell tput init)
APP := skaben_device

build:  ## Собрать контейнер для линтера и тестов
	@docker-compose build --no-cache

test:  ## Запустить тест переданный аргументом [tests=[test_00_test]]
	@docker-compose run --rm ${APP} sh -c pytest tests

lint:  ## Запустить линтер
	@docker-compose run --rm ${APP} ./run-lint.sh

help:
	@echo "\nКоманды:\n"
	@grep -E '^[a-zA-Z.%_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%2s$(ACCENT)%-20s${RESET} %s\n", " ", $$1, $$2}'
	@echo ""
