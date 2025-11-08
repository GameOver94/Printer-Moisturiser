# PowerShell test script for the printer maintenance application
# This script helps test the application without Docker on Windows

Write-Host '==========================================' -ForegroundColor Cyan
Write-Host 'Printer Maintenance Application Test' -ForegroundColor Cyan
Write-Host '==========================================' -ForegroundColor Cyan
Write-Host ''

# Check if .venv exists
$venvPath = Join-Path $PSScriptRoot ".venv"
if (-Not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found at: $venvPath" -ForegroundColor Yellow
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-Host "Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "Could not find activation script at: $activateScript" -ForegroundColor Red
    exit 1
}
Write-Host '' 

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
$requirementsPath = Join-Path $PSScriptRoot "requirements.txt"
# Ensure build tools are up-to-date to avoid build-time failures
Write-Host "Upgrading build tools (pip, setuptools, wheel, setuptools_scm)..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel setuptools_scm
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to upgrade build tools" -ForegroundColor Red
    exit 1
}
Write-Host "Build tools upgraded" -ForegroundColor Green

# Install requirements (quiet)
python -m pip install -q -r $requirementsPath
if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "Failed to install dependencies" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Set default environment variables for testing
if (-Not $env:PRINTER_IP) { $env:PRINTER_IP = "192.168.1.100" }
if (-Not $env:NTFY_CHANNEL) { $env:NTFY_CHANNEL = "printer-test" }
if (-Not $env:PRINTER_NAME) { $env:PRINTER_NAME = "HP Smart Tank 7005" }
if (-Not $env:SNMP_COMMUNITY) { $env:SNMP_COMMUNITY = "public" }
if (-Not $env:OUTPUT_PATH) { $env:OUTPUT_PATH = "$env:TEMP\printer-test.pdf" }

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  PRINTER_IP: $env:PRINTER_IP"
Write-Host "  NTFY_CHANNEL: $env:NTFY_CHANNEL"
Write-Host "  PRINTER_NAME: $env:PRINTER_NAME"
Write-Host "  SNMP_COMMUNITY: $env:SNMP_COMMUNITY"
Write-Host "  OUTPUT_PATH: $env:OUTPUT_PATH"
Write-Host ""

# Run the application
Write-Host "Running printer maintenance application..." -ForegroundColor Yellow
Write-Host '==========================================' -ForegroundColor Cyan
$srcPath = Join-Path $PSScriptRoot "src"
Push-Location $srcPath
python main.py
$exitCode = $LASTEXITCODE
Pop-Location

Write-Host ''
Write-Host '==========================================' -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "Test completed successfully!" -ForegroundColor Green
    Write-Host "Generated PDF: $env:OUTPUT_PATH" -ForegroundColor Green
} else {
    Write-Host "Test failed with exit code: $exitCode" -ForegroundColor Red
}
Write-Host '==========================================' -ForegroundColor Cyan

exit $exitCode
