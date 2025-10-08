# Start ActivityGuide Backend Server
# Run this script to start the FastAPI backend

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "  STARTING ACTIVITYGUIDE BACKEND SERVER" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "app/main.py")) {
    Write-Host "[ERROR] Please run this script from the ActivityGuide root directory" -ForegroundColor Red
    exit 1
}

# Check Python
Write-Host "[INFO] Checking Python..." -ForegroundColor Yellow
python --version

# Check if dependencies are installed
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
    
    # Check API keys
    $content = Get-Content ".env" -Raw
    if ($content -match "YELP_API_KEY=(\w+)") {
        Write-Host "[OK] Yelp API key configured" -ForegroundColor Green
    }
    if ($content -match "EVENTBRITE_API_KEY=(\w+)") {
        Write-Host "[OK] Eventbrite API key configured" -ForegroundColor Green
    }
} else {
    Write-Host "[ERROR] .env file not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host "  STARTING SERVER ON http://localhost:8000" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 78) -ForegroundColor Cyan
Write-Host ""
Write-Host "[INFO] Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "[INFO] API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "[INFO] Alternative Docs: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
