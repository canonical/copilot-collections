# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

# Makefile for markdown linting

# Variables
VENVDIR := .venv
CONFIG := .pymarkdown.json
SOURCEDIR ?= .

# Phony targets
.PHONY: help lint-md clean venv pymarkdownlnt-install

# Default target
help:
	@echo "Available targets:"
	@echo "  venv                - Create virtual environment using uv"
	@echo "  pymarkdownlnt-install - Install pymarkdownlnt"
	@echo "  lint-md             - Run markdown linter"
	@echo "  clean               - Remove virtual environment"

# Create virtual environment using uv
venv:
	@if [ ! -d "$(VENVDIR)" ]; then \
		echo "Creating virtual environment with uv..."; \
		uv venv $(VENVDIR); \
		echo "Virtual environment created at $(VENVDIR)"; \
	fi

# Install pymarkdownlnt
pymarkdownlnt-install: venv
	@uv pip install --python $(VENVDIR) pymarkdownlnt --quiet 2>&1 | grep -v "Audited" || true

# Run markdown linter
lint-md: pymarkdownlnt-install
	@echo "Running markdown linter..."
	@uv run --python $(VENVDIR) pymarkdownlnt --config $(CONFIG) scan --recurse $(SOURCEDIR)

# Clean virtual environment
clean:
	@echo "Removing virtual environment..."
	@rm -rf $(VENVDIR)
	@echo "Virtual environment removed"
