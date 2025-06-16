# SEO Auditing Solution - Development Makefile

.PHONY: help install test test-unit test-integration test-api test-services test-seo test-tasks test-coverage test-watch clean lint format type-check dev build run stop logs shell db-shell test-db setup-dev docker-build docker-run docker-stop docker-clean

# Default target
help:
	@echo "SEO Auditing Solution - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install        Install dependencies"
	@echo "  setup-dev      Complete development setup"
	@echo "  dev            Start development server"
	@echo "  shell          Open Python shell with app context"
	@echo ""
	@echo "Testing:"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-api       Run API tests only"
	@echo "  test-services  Run service layer tests only"
	@echo "  test-seo       Run SEO analyzer tests only"
	@echo "  test-tasks     Run background task tests only"
	@echo "  test-coverage  Run tests with coverage report"
	@echo "  test-watch     Run tests in watch mode"
	@echo ""
	@echo "Quality:"
	@echo "  lint           Run linting checks"
	@echo "  format         Format code"
	@echo "  type-check     Run type checking"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   Build Docker containers"
	@echo "  docker-run     Start Docker stack"
	@echo "  docker-stop    Stop Docker stack"
	@echo "  docker-clean   Clean Docker resources"
	@echo ""
	@echo "Database:"
	@echo "  db-shell       Open database shell"
	@echo "  test-db        Reset test database"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          Clean cache and temporary files"
	@echo "  logs           Show application logs"

# Development setup
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

setup-dev: install
	@echo "Setting up development environment..."
	@echo "Creating test database..."
	@mkdir -p tests/data
	@echo "Development setup complete!"

# Development server
dev:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

shell:
	python -c "from app.database import get_db; from app import models; print('Database models loaded. Use models.<ModelName> to access.')"

# Testing
test:
	pytest tests/ -v

test-unit:
	pytest tests/ -v -m "unit"

test-integration:
	pytest tests/ -v -m "integration"

test-api:
	pytest tests/test_api.py -v

test-services:
	pytest tests/test_services.py -v

test-seo:
	pytest tests/test_seo_analyzers.py -v

test-tasks:
	pytest tests/test_background_tasks.py -v

test-models:
	pytest tests/test_models.py -v

test-coverage:
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80

test-watch:
	pytest-watch tests/ -- -v

# Quality checks
lint:
	flake8 app/ tests/ main.py
	black --check app/ tests/ main.py
	isort --check-only app/ tests/ main.py

format:
	black app/ tests/ main.py
	isort app/ tests/ main.py

type-check:
	mypy app/

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

build:
	docker-compose build app

run:
	docker-compose up -d

stop:
	docker-compose down

logs:
	docker-compose logs app --tail=50 -f

# Database
db-shell:
	docker-compose exec postgres psql -U seo_user -d seo_auditing

test-db:
	@echo "Resetting test database..."
	@rm -f test.db
	@echo "Test database reset complete!"

# Utilities
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -f test.db

# Development workflow shortcuts
quick-test: test-unit test-api
	@echo "Quick tests completed!"

full-test: test-coverage lint type-check
	@echo "Full test suite completed!"

pre-commit: format lint test-unit
	@echo "Pre-commit checks completed!"

# Health checks
health:
	curl -f http://localhost:8000/health || echo "Service not running"

api-docs:
	@echo "API documentation available at: http://localhost:8000/docs"
	@echo "ReDoc documentation available at: http://localhost:8000/redoc"

# Deployment helpers
check-deps:
	pip-audit
	safety check

update-deps:
	pip-compile requirements.in
	pip-compile requirements-dev.in

# Performance testing
test-performance:
	@echo "Running performance tests..."
	pytest tests/test_integration.py::TestPerformanceBaseline -v

# Database migrations (if using Alembic)
migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

# Monitoring and debugging
debug:
	python -m debugpy --listen 5678 --wait-for-client -m uvicorn main:app --reload

profile:
	python -m cProfile -o profile_output.prof main.py

# Documentation
docs-serve:
	@echo "Serving API documentation at http://localhost:8000/docs"
	@echo "ReDoc available at http://localhost:8000/redoc"

# Environment checks
check-env:
	@echo "Python version: $(shell python --version)"
	@echo "Pip version: $(shell pip --version)"
	@echo "FastAPI version: $(shell python -c 'import fastapi; print(fastapi.__version__)')"
	@echo "SQLAlchemy version: $(shell python -c 'import sqlalchemy; print(sqlalchemy.__version__)')"
	@echo "Pytest version: $(shell python -c 'import pytest; print(pytest.__version__)')"

# CI/CD helpers
ci-test:
	pytest tests/ --junitxml=test-results.xml --cov=app --cov-report=xml

ci-build:
	docker build -t seo-auditing-solution .

ci-security:
	bandit -r app/
	safety check

# Load testing (if locust is installed)
load-test:
	locust -f tests/load_test.py --host=http://localhost:8000

# Backup and restore
backup-db:
	docker-compose exec postgres pg_dump -U seo_user seo_auditing > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db:
	@read -p "Enter backup file path: " backup_file; \
	docker-compose exec -T postgres psql -U seo_user seo_auditing < $$backup_file