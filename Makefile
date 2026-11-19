# Copyright 2026 Canonical Ltd.
# See LICENSE file for licensing details.

# Makefile for project linting and formatting

# Variables
VENVDIR := .venv
CONFIG := .pymarkdown.json
SOURCEDIR ?= .

# Phony targets
.PHONY: help lint-md clean venv pymarkdownlnt-install lint-sh format-sh

# Default target
help:
	@echo "Available targets:"
	@echo "  venv                  - Create virtual environment using uv"
	@echo "  pymarkdownlnt-install - Install pymarkdownlnt"
	@echo "  lint-md               - Run markdown linter"
	@echo "  lint-sh               - Lint shell scripts (shellcheck and shfmt)"
	@echo "  format-sh             - Format shell scripts using shfmt"
	@echo "  clean                 - Remove virtual environment"

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

# Format shell scripts
format-sh:
	@# jinja2 shell script templates are mistakenly counted as "true" shell scripts due to their shebang,
	@# so explicitly filter them out
	@echo "Formatting shell scripts with shfmt..."
	@git ls-files -z | xargs -0 sh -c 'for f; do case "$$f" in *.sh.j2) continue;; esac; file --mime-type -Nn -- "$$f" | grep -q shellscript && printf "%s\0" "$$f"; done' -- | xargs -0r shfmt -w

# Lint shell scripts
lint-sh:
	@echo "Running shell linters..."
	@# jinja2 shell script templates are mistakenly counted as "true" shell scripts due to their shebang,
	@# so explicitly filter them out
	@git ls-files -z | xargs -0 sh -c 'for f; do case "$$f" in *.sh.j2) continue;; esac; file --mime-type -Nn -- "$$f" | grep -q shellscript && printf "%s\0" "$$f"; done' -- | xargs -0r shfmt --diff
	@git ls-files -z | xargs -0 sh -c 'for f; do case "$$f" in *.sh.j2) continue;; esac; file --mime-type -Nn -- "$$f" | grep -q shellscript && printf "%s\0" "$$f"; done' -- | xargs -0r shellcheck

