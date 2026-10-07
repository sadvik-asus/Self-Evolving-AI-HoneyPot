.PHONY: install test run-dashboard run-ssh

install:
	pip install -r requirements.txt

test:
	pytest

run-dashboard:
	python -m backend.api.web_app

run-ssh:
	python -m backend.ssh.server
