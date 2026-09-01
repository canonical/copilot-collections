# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

# Makefile for markdown linting

# Variables
VENVDIR := .venv
CONFIG := .pymarkdown.json
SOURCEDIR ?= .
FILE ?=

# Phony targets
.PHONY: help lint-md clean venv pymarkdownlnt-install preview

# Default target
help:
	@echo "Available targets:"
	@echo "  venv                - Create virtual environment using uv"
	@echo "  pymarkdownlnt-install - Install pymarkdownlnt"
	@echo "  lint-md             - Run markdown linter (FILE=path/to/file.md to check a single file)"
	@echo "  preview             - Preview files that would be installed for a collection (COLLECTION=name)"
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
# Usage: make lint-md [FILE=path/to/file.md] [SOURCEDIR=path/to/dir]
lint-md: pymarkdownlnt-install
	@echo "Running markdown linter..."
	@if [ -n "$(FILE)" ]; then \
		uv run --python $(VENVDIR) pymarkdownlnt --config $(CONFIG) scan $(FILE); \
	else \
		uv run --python $(VENVDIR) pymarkdownlnt --config $(CONFIG) scan --recurse $(SOURCEDIR); \
	fi

# Clean virtual environment
clean:
	@echo "Removing virtual environment..."
	@rm -rf $(VENVDIR)
	@echo "Virtual environment removed"

# Preview what would be installed for a given collection (dry-run)
# Usage: make preview COLLECTION=<collection-name>
COLLECTION ?=
preview:
	@if [ -z "$(COLLECTION)" ]; then \
		echo "❌ Usage: make preview COLLECTION=<collection-name>"; \
		exit 1; \
	fi
	@TMPFILE=$$(mktemp ./copilot-preview-XXXXXX.yaml) && \
	printf 'copilot:\n  collections:\n    - %s\n' "$(COLLECTION)" > $$TMPFILE && \
	echo "🔍 Previewing collection: $(COLLECTION)" && \
	bash scripts/install_collections.sh $$TMPFILE . --dry-run; \
	rm -f $$TMPFILE
