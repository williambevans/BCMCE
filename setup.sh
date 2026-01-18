#!/bin/bash
# BCMCE Platform Quick Setup Script
# HH Holdings LLC / Bevans Real Estate

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║   ██╗  ██╗    ██╗  ██╗          ██╗  ██╗ ██████╗ ██╗         ║"
echo "║   ██║  ██║    ██║  ██║          ██║  ██║██╔═══██╗██║         ║"
echo "║   ███████║    ███████║          ███████║██║   ██║██║         ║"
echo "║   ██╔══██║    ██╔══██║          ██╔══██║██║   ██║██║         ║"
echo "║   ██║  ██║    ██║  ██║          ██║  ██║╚██████╔╝███████╗    ║"
echo "║   ╚═╝  ╚═╝    ╚═╝  ╚═╝          ╚═╝  ╚═╝ ╚═════╝ ╚══════╝    ║"
echo "║                                                                ║"
echo "║   BCMCE Platform Setup                                        ║"
echo "║   Bosque County Mineral & Commodities Exchange                ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✅ Docker found: $(docker --version)"

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✅ Docker Compose found: $(docker-compose --version)"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11 or higher:"
    echo "   https://www.python.org/downloads/"
    exit 1
fi
echo "✅ Python found: $(python3 --version)"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip not found. Please install pip first."
    exit 1
fi
echo "✅ pip found: $(pip3 --version)"

echo ""
echo "📦 Setting up BCMCE Platform..."
echo ""

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env configuration file..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env with your configuration before starting:"
    echo "   - Database credentials"
    echo "   - Secret keys"
    echo "   - SMTP settings (for notifications)"
    echo ""
    read -p "Press Enter to continue after editing .env, or Ctrl+C to exit..."
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip3 install -q -r requirements.txt
cd ..
echo "✅ Python dependencies installed"

# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p data/backups
mkdir -p logs
echo "✅ Directories created"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  ✅ BCMCE Platform setup complete!                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 Quick Start:"
echo ""
echo "   Development:"
echo "   $ ./start-dev.sh"
echo "   $ cd backend && python main.py"
echo ""
echo "   Production:"
echo "   $ ./start-production.sh"
echo ""
echo "   Using Make:"
echo "   $ make setup-dev    # Setup development environment"
echo "   $ make docker-up    # Start services"
echo "   $ make dev          # Run backend API"
echo ""
echo "📚 Documentation:"
echo "   - API docs:       docs/API.md"
echo "   - Deployment:     docs/DEPLOYMENT.md"
echo "   - Getting Started: docs/GETTING_STARTED.md"
echo ""
echo "🌐 Once running:"
echo "   - API:          http://localhost:8000"
echo "   - API Docs:     http://localhost:8000/api/docs"
echo "   - Landing Page: Open index.html in browser"
echo ""
echo "💡 Need help? Run: make help"
echo ""
