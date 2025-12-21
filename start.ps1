# MISoft Application Startup Script
# This script starts both the Django backend and Vite frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   MISoft Application Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is running
Write-Host "Checking PostgreSQL service..." -ForegroundColor Yellow
$postgresService = Get-Service -Name "*postgres*" -ErrorAction SilentlyContinue | Where-Object {$_.Status -eq 'Running'}

if ($postgresService) {
    Write-Host "✅ PostgreSQL is running ($($postgresService.DisplayName))" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL is not running!" -ForegroundColor Red
    Write-Host "Please start PostgreSQL service and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Start Django backend in a new window
$backendPath = Join-Path $PSScriptRoot "backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; .\venv_new\Scripts\Activate.ps1; Write-Host 'Starting Django Backend Server...' -ForegroundColor Green; python manage.py runserver"

Write-Host "✅ Backend server starting in new window..." -ForegroundColor Green
Write-Host "   URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

# Wait a bit for backend to start
Write-Host "Waiting 5 seconds for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Start Vite frontend in a new window
$frontendPath = Join-Path $PSScriptRoot "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host 'Starting Vite Frontend Server...' -ForegroundColor Green; npm run dev"

Write-Host "✅ Frontend server starting in new window..." -ForegroundColor Green
Write-Host "   URL: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Application Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your application at:" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "  Admin:    http://localhost:8000/admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
