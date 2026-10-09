.PHONY: install test lint run-dashboard run-ssh docker-up docker-down

install:
	pip install -r requirements.txt

test:
	pytest

lint:
	black .
	pylint backend tests

run-dashboard:
	python -m backend.api.web_app

run-ssh:
	python -m backend.ssh.server

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
