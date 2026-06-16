<#
.SYNOPSIS
Builds the NeuralRadar Windows executable using PyInstaller.

.DESCRIPTION
This script prepares the build environment, installs dependencies, and packages NeuralRadar into a one-folder distribution.
#>

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host " NeuralRadar Windows Internal Build Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running from project root
if (-not (Test-Path "app\main.py")) {
    Write-Host "[-] Error: app\main.py not found. Please run this script from the project root." -ForegroundColor Red
    exit 1
}

# Check for virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "[-] Error: .venv folder not found." -ForegroundColor Red
    Write-Host "    Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "    python -m venv .venv" -ForegroundColor Yellow
    Write-Host "    .\.venv\Scripts\activate" -ForegroundColor Yellow
    exit 1
}

# Ensure we're using the venv python if running outside activated shell but inside project root
$PythonPath = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $PythonPath)) {
    Write-Host "[-] Error: Python executable not found in .venv\Scripts\" -ForegroundColor Red
    exit 1
}

Write-Host "[+] Installing runtime dependencies..." -ForegroundColor Green
& $PythonPath -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Error installing runtime dependencies." -ForegroundColor Red
    exit 1
}

Write-Host "[+] Installing development dependencies..." -ForegroundColor Green
& $PythonPath -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Error installing development dependencies." -ForegroundColor Red
    exit 1
}

Write-Host "[+] Cleaning previous builds..." -ForegroundColor Green
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

Write-Host "[+] Building NeuralRadar executable (one-folder mode)..." -ForegroundColor Green
$PyInstallerArgs = @(
    "--noconfirm",
    "--onedir",
    "--windowed",
    "--name", "NeuralRadar"
)

if (Test-Path "app\assets\icons\neuralradar.ico") {
    $PyInstallerArgs += "--icon=app\assets\icons\neuralradar.ico"
    Write-Host "    Found icon, applying..." -ForegroundColor Yellow
}

$PyInstallerArgs += "app\main.py"

& ".\.venv\Scripts\pyinstaller.exe" $PyInstallerArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[+] Build successful!" -ForegroundColor Green
    Write-Host "    Executable located at: dist\NeuralRadar\NeuralRadar.exe" -ForegroundColor Yellow
} else {
    Write-Host "`n[-] Build failed with exit code $LASTEXITCODE." -ForegroundColor Red
}
