# BCMCE Platform Makefile
# HH Holdings LLC / Bevans Real Estate

.PHONY: help install dev start stop test clean docker-build docker-up docker-down

help:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║  BCMCE Platform - Development Commands                        ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "  make install      - Install backend dependencies"
	@echo "  make dev          - Run backend in development mode"
	@echo "  make start        - Start all services with Docker Compose"
	@echo "  make stop         - Stop all Docker services"
	@echo "  make test         - Run backend tests"
	@echo "  make clean        - Clean up generated files"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start Docker services"
	@echo "  make docker-down  - Stop Docker services"
	@echo "  make logs         - View Docker logs"
	@echo "  make db-migrate   - Run database migrations"
	@echo "  make db-seed      - Seed database with initial data"
	@echo ""

install:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt

dev:
	@echo "🚀 Starting backend in development mode..."
	cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

start: docker-up

stop: docker-down

test:
	@echo "🧪 Running backend tests..."
	cd backend && pytest tests/ -v

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "   API:        http://localhost:8000"
	@echo "   API Docs:   http://localhost:8000/api/docs"
	@echo "   PostgreSQL: localhost:5432"
	@echo "   Redis:      localhost:6379"

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

logs:
	@echo "📋 Viewing Docker logs..."
	docker-compose logs -f

db-migrate:
	@echo "🗄️  Running database migrations..."
	docker-compose exec postgres psql -U bcmce -d bcmce_db -f /docker-entrypoint-initdb.d/001_create_tables.sql

db-seed:
	@echo "🌱 Seeding database..."
	cd backend && python -c "from database import seed_database; seed_database()"

format:
	@echo "🎨 Formatting code..."
	cd backend && black . && isort .

lint:
	@echo "🔍 Linting code..."
	cd backend && flake8 . && mypy .

setup-dev: install
	@echo "⚙️  Setting up development environment..."
	cp -n .env.example .env || true
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "📝 Next steps:"
	@echo "   1. Edit .env with your configuration"
	@echo "   2. Run 'make docker-up' to start services"
	@echo "   3. Run 'make db-migrate' to set up database"
	@echo "   4. Run 'make db-seed' to add sample data"
	@echo "   5. Open http://localhost:8000/api/docs"
