# Makefile for development.
VIRTUALENV = virtualenv
VENV := $(shell echo $${VIRTUAL_ENV-.venv})
ROOT_DIR := $(shell pwd)
PYTHON = $(VENV)/bin/python
NOSE = $(VENV)/bin/nosetests

DEV_STAMP = $(VENV)/.dev_env_installed.stamp
INSTALL_STAMP = $(VENV)/.install.stamp

PROJECT = $(shell $(PYTHON) -c "import setup; print(setup.NAME)")

.IGNORE: clean
.PHONY: all install virtualenv tests


all: install
develop: install-dev

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): $(PYTHON) setup.py
	$(VENV)/bin/pip install -Ue .
	touch $(INSTALL_STAMP)

install-dev: $(INSTALL_STAMP) $(DEV_STAMP)
$(DEV_STAMP): $(PYTHON) dev-requirements.txt
	$(VENV)/bin/pip install -Ur dev-requirements.txt
	touch $(DEV_STAMP)

virtualenv: $(PYTHON)
$(PYTHON):
	virtualenv $(VENV)

clean:
	find $(ROOT_DIR)/ -name "*.pyc" -delete
	find $(ROOT_DIR)/ -name ".noseids" -delete


distclean: clean
	rm -rf $(ROOT_DIR)/*.egg-info

test: install-dev
	$(NOSE) --config $(ROOT_DIR)/etc/nose.cfg $(PROJECT)
	rm -f $(ROOT_DIR)/.coverage
