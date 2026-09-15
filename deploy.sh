#!/usr/bin/env bash
# =================================================================
# TruthGuard — Automated Docker Deployment Script (Linux / macOS)
# =================================================================

set -e

echo "======================================================"
echo "🛡️  TruthGuard Production Deployment"
echo "======================================================"

# 1. Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed. Please install Docker first."; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "❌ Docker Compose is not installed."; exit 1; }

# 2. Environment file check
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
fi

# 3. Create persistent data directories
mkdir -p data

# 4. Build and run containers
echo "🚀 Building and launching containers..."
docker compose down --remove-orphans
docker compose up -d --build

# 5. Wait for health check
echo "⏳ Awaiting backend service readiness..."
MAX_RETRIES=30
COUNT=0
until curl -sf http://localhost:8000/api/health >/dev/null 2>&1 || [ $COUNT -eq $MAX_RETRIES ]; do
    sleep 2
    COUNT=$((COUNT + 1))
    echo -n "."
done

echo ""
if [ $COUNT -lt $MAX_RETRIES ]; then
    echo "✅ TruthGuard deployed successfully!"
    echo "🌐 Frontend Dashboard: http://localhost:3000"
    echo "🔌 Backend REST API:   http://localhost:8000"
    echo "📖 Interactive Docs:   http://localhost:8000/docs"
else
    echo "⚠️  Backend took longer than expected to report healthy. Check logs with: docker compose logs backend"
fi
