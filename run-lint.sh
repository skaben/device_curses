#!/usr/bin/env bash

set -e
echo -e "Running linting checks..."
ruff check --no-cache --verbose .
ruff format --no-cache --verbose .
