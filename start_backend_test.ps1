# Start backend for testing
cd C:\code\ActivityGuide
Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host "This will run in foreground - press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --reload --port 8000 --log-level info

