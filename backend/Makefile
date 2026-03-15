.PHONY: dev test lint

dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest

lint:
	python -m compileall app main.py

