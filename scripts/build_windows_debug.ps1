<#
.SYNOPSIS
Builds a Debug NeuralRadar Windows executable using PyInstaller.

.DESCRIPTION
This script prepares the build environment, installs dependencies, and packages NeuralRadar into a one-folder distribution WITH the console window enabled to view tracebacks.
#>

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host " NeuralRadar Windows Internal DEBUG Build Script" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
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

Write-Host "[+] Cleaning previous debug builds..." -ForegroundColor Green
if (Test-Path "build\NeuralRadar-Debug") { Remove-Item -Recurse -Force "build\NeuralRadar-Debug" }
if (Test-Path "dist\NeuralRadar-Debug") { Remove-Item -Recurse -Force "dist\NeuralRadar-Debug" }

Write-Host "[+] Building NeuralRadar DEBUG executable (one-folder mode, console enabled)..." -ForegroundColor Green
$PyInstallerArgs = @(
    "--noconfirm",
    "--onedir",
    "--name", "NeuralRadar-Debug"
)

if (Test-Path "app\assets\icons\neuralradar.ico") {
    $PyInstallerArgs += "--icon=app\assets\icons\neuralradar.ico"
    Write-Host "    Found icon, applying..." -ForegroundColor Yellow
}

$PyInstallerArgs += "app\main.py"

& ".\.venv\Scripts\pyinstaller.exe" $PyInstallerArgs

if ($LASTEXITCODE -eq 0) {
    # Rename executable to NeuralRadar.exe as requested
    Rename-Item "dist\NeuralRadar-Debug\NeuralRadar-Debug.exe" "NeuralRadar.exe"
    
    Write-Host "`n[+] Build successful!" -ForegroundColor Green
    Write-Host "    Debug Executable located at: dist\NeuralRadar-Debug\NeuralRadar.exe" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "    Run:" -ForegroundColor Yellow
    Write-Host "    .\dist\NeuralRadar-Debug\NeuralRadar.exe" -ForegroundColor Yellow
} else {
    Write-Host "`n[-] Build failed with exit code $LASTEXITCODE." -ForegroundColor Red
}
