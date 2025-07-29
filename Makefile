# Makefile for Football Stats Application
# Provides convenient commands for development tasks

.PHONY: help install lint format type-check security clean test docker-build docker-up docker-down

# Default target
help:
	@echo "Football Stats Application - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install     - Install all dependencies"
	@echo "  make install-dev - Install development dependencies"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  make lint        - Run all linting tools"
	@echo "  make format      - Format code with black and isort"
	@echo "  make format-check- Check if code formatting is correct"
	@echo "  make type-check  - Run mypy type checking"
	@echo "  make style-check - Run flake8 style checking"
	@echo "  make security    - Run bandit security analysis"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-build- Build Docker containers"
	@echo "  make docker-up   - Start the application with Docker"
	@echo "  make docker-down - Stop Docker containers"
	@echo "  make docker-logs - View Docker container logs"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean       - Clean up temporary files"
	@echo "  make test        - Run tests (when implemented)"

# Installation commands
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install mypy flake8 bandit black isort pre-commit

# Code formatting
format:
	@echo "🎨 Formatting code with black..."
	black app/ import_players.py
	@echo "📦 Sorting imports with isort..."
	isort app/ import_players.py
	@echo "✅ Code formatting complete!"

format-check:
	@echo "🔍 Checking code formatting..."
	black --check --diff app/ import_players.py
	isort --check-only --diff app/ import_players.py

# Individual linting tools
type-check:
	@echo "🔍 Running MyPy type checking..."
	mypy app/ import_players.py

style-check:
	@echo "🔍 Running Flake8 style checking..."
	flake8 app/ import_players.py

security:
	@echo "🔒 Running Bandit security analysis..."
	bandit -r app/ import_players.py

# Comprehensive linting
lint:
	@echo "🔍 Running comprehensive linting..."
	@./lint.sh

# Docker commands
docker-build:
	@echo "🐳 Building Docker containers..."
	docker-compose build

docker-up:
	@echo "🚀 Starting application with Docker..."
	docker-compose up

docker-up-detached:
	@echo "🚀 Starting application with Docker (detached)..."
	docker-compose up -d

docker-down:
	@echo "🛑 Stopping Docker containers..."
	docker-compose down

docker-logs:
	@echo "📋 Viewing Docker logs..."
	docker-compose logs -f

docker-clean:
	@echo "🧹 Cleaning up Docker resources..."
	docker-compose down -v
	docker system prune -f

# Testing (placeholder for future implementation)
test:
	@echo "🧪 Running tests..."
	@echo "Tests not yet implemented. Add pytest and test files."

# Cleanup
clean:
	@echo "🧹 Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Pre-commit setup
setup-pre-commit:
	@echo "🔧 Setting up pre-commit hooks..."
	pre-commit install
	pre-commit run --all-files

# Development environment setup
setup-dev: install-dev setup-pre-commit
	@echo "🎉 Development environment setup complete!"
	@echo "Run 'make help' to see available commands."
