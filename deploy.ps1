# =================================================================
# TruthGuard — Automated Docker Deployment Script (Windows PowerShell)
# =================================================================

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "🛡️  TruthGuard Production Deployment" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# 1. Check prerequisites
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed or not in PATH." -ForegroundColor Red
    Exit 1
}

# 2. Check .env file
if (-not (Test-Path ".env")) {
    Write-Host "📋 Copying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

# 3. Create persistent data folder
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" | Out-Null
}

# 4. Build and run containers
Write-Host "🚀 Building and starting containers..." -ForegroundColor Green
docker compose down --remove-orphans
docker compose up -d --build

# 5. Check health
Write-Host "⏳ Waiting for backend healthcheck..." -ForegroundColor Yellow
$maxRetries = 30
$count = 0
$healthy = $false

while ($count -lt $maxRetries -and -not $healthy) {
    Start-Sleep -Seconds 2
    $count++
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.status -eq "ok") {
            $healthy = $true
        }
    } catch {
        Write-Host "." -NoNewline
    }
}

Write-Host ""
if ($healthy) {
    Write-Host "✅ TruthGuard deployed successfully!" -ForegroundColor Green
    Write-Host "🌐 Frontend Dashboard: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "🔌 Backend REST API:   http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📖 Interactive Docs:   http://localhost:8000/docs" -ForegroundColor Cyan
} else {
    Write-Host "⚠️ Backend is taking longer than expected. Check logs with: docker compose logs backend" -ForegroundColor Yellow
}
