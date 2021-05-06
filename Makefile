# -*- coding: utf-8 -*-

# =============
# Configuration
# =============

$(eval venv             := .venv)
$(eval pip              := $(venv)/bin/pip)
$(eval python           := $(venv)/bin/python)
$(eval pytest           := $(venv)/bin/pytest)



# =====
# Setup
# =====

# Setup Python virtualenv.
setup-virtualenv:
	test -e $(python) || python3 -m venv $(venv)

# Install requirements for building the documentation.
setup-requirements: setup-virtualenv
	$(pip) install --requirement=requirements.txt


# ====
# Main
# ====
test: setup-requirements
	$(pytest) tests -vvv --diff-type=unified --no-hints

test-trouble: setup-requirements
	$(pytest) tests -vvv --diff-type=unified --no-hints -k "cratedb and ddpsql and fast"
