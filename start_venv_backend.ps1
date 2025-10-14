# Start ActivityGuide Backend Using VENV
# This script activates the virtual environment and runs the backend

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "  STARTING BACKEND WITH VENV" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "[INFO] Run: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Activate venv
Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Check if in correct directory
if (-not (Test-Path "app/main.py")) {
    Write-Host "[ERROR] Please run this script from the ActivityGuide root directory" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "[INFO] Checking dependencies..." -ForegroundColor Yellow
python -c "import fastapi; import uvicorn; print('[OK] FastAPI and Uvicorn installed')" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Dependencies not installed!" -ForegroundColor Red
    Write-Host "[INFO] Run: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Check database
Write-Host "[INFO] Checking database..." -ForegroundColor Yellow
if (Test-Path "activityguide.db") {
    Write-Host "[OK] Database file exists" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Database file not found - will be created on first run" -ForegroundColor Yellow
}

# Check .env file
Write-Host "[INFO] Checking .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "[OK] .env file exists" -ForegroundColor Green
} else {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "  SERVER STARTING ON http://localhost:8000" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Using: " -NoNewline -ForegroundColor Yellow
python -c "import sys; print(sys.executable)"
Write-Host "[INFO] Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "[INFO] API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "[INFO] Alternative Docs: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

