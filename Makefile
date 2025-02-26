.PHONY: help install migrate run test clean init docker-build docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make migrate       - Run database migrations"
	@echo "  make run           - Run development server"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Remove Python file artifacts"
	@echo "  make init          - Initialize database with default data"
	@echo "  make docker-build  - Build Docker containers"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"

install:
	pip install -r requirements.txt

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	python manage.py runserver

test:
	python manage.py test

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete
	rm -rf *.egg-info
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

init:
	python initialize_data.py

docker-build:
	docker-compose build

docker-up:
	docker-compose up

docker-down:
	docker-compose down
