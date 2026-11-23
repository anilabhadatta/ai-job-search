# PowerShell Runner for AI Job Search
Set-Location $PSScriptRoot

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Starting AI Job Search Web App" -ForegroundColor Green
Write-Host "  Local URL: http://localhost:5000/ai-job-search" -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan

$VenvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"

if (Test-Path $VenvPython) {
    & $VenvPython run_web.py @args
} else {
    python run_web.py @args
}
