"""
Unit and integration tests for Phase 13: Deployment & Production Readiness.
Validates containerization files, reverse-proxy configs, environment manifests,
and production security headers.
"""

import os
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

WORKSPACE_ROOT = Path(__file__).parent.parent


def test_deployment_artifacts_exist():
    """Verify all production deployment files exist in the repository."""
    required_files = [
        WORKSPACE_ROOT / "backend" / "Dockerfile",
        WORKSPACE_ROOT / "frontend" / "Dockerfile",
        WORKSPACE_ROOT / "frontend" / "nginx.conf",
        WORKSPACE_ROOT / "docker-compose.yml",
        WORKSPACE_ROOT / ".env.example",
        WORKSPACE_ROOT / "deploy.sh",
        WORKSPACE_ROOT / "deploy.ps1",
    ]
    for file_path in required_files:
        assert file_path.exists(), f"Missing required deployment file: {file_path}"
        assert file_path.stat().st_size > 0, f"File is empty: {file_path}"


def test_docker_compose_configuration():
    """Verify docker-compose.yml contains required services, healthchecks, and volume mappings."""
    compose_path = WORKSPACE_ROOT / "docker-compose.yml"
    content = compose_path.read_text(encoding="utf-8")

    # Assert services
    assert "backend:" in content
    assert "frontend:" in content
    assert "truthguard-backend" in content
    assert "truthguard-frontend" in content

    # Assert ports
    assert '"8000:8000"' in content
    assert '"3000:80"' in content

    # Assert healthcheck and persistent volumes
    assert "healthcheck:" in content
    assert "truthguard-data:" in content
    assert "truthguard-network" in content


def test_frontend_nginx_configuration():
    """Verify nginx.conf contains SPA routing and API reverse-proxy definitions."""
    nginx_path = WORKSPACE_ROOT / "frontend" / "nginx.conf"
    content = nginx_path.read_text(encoding="utf-8")

    assert "try_files $uri $uri/ /index.html;" in content
    assert "location /api/" in content
    assert "proxy_pass http://backend:8000/api/;" in content
    assert "client_max_body_size" in content
    assert "gzip on;" in content


def test_backend_dockerfile_configuration():
    """Verify backend Dockerfile uses multi-stage builds and sets up system dependencies."""
    dockerfile_path = WORKSPACE_ROOT / "backend" / "Dockerfile"
    content = dockerfile_path.read_text(encoding="utf-8")

    assert "FROM python:3.11-slim" in content
    assert "tesseract-ocr" in content
    assert "HEALTHCHECK" in content
    assert "EXPOSE 8000" in content


@pytest.mark.asyncio
async def test_api_security_headers_and_health():
    """Verify production security headers and database status on /api/health."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["project"] == "TruthGuard"
        assert data["database"] == "connected"

        # Assert security headers injected by middleware
        headers = response.headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "DENY"
        assert headers.get("X-XSS-Protection") == "1; mode=block"
        assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
