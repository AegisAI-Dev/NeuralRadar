# Building NeuralRadar for Windows

This document explains how to create an internal Windows executable (.exe) for NeuralRadar using PyInstaller.

⚠️ **Note:** This is an internal smoke-test build process. It is used to verify packaging works correctly before the final public release.

## Prerequisites
- Windows 10/11
- Python 3.10+ installed and added to PATH
- Project source code

## 1. Create and Activate Virtual Environment
You must build NeuralRadar from within an isolated virtual environment to avoid bundling unnecessary system packages.

Open PowerShell in the project root and run:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

## 2. Install Dependencies
Install both the runtime dependencies and the development dependencies (which includes PyInstaller):
```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## 3. Run the Build Script
We use a PowerShell script to automate the build process. This script cleans old builds and runs PyInstaller in one-folder mode.
```powershell
.\scripts\build_windows.ps1
```

## 4. Locating the Executable
Once the build completes successfully, the compiled application will be located at:
`dist\NeuralRadar\NeuralRadar.exe`

## 5. Packaged Data and Logs
When running NeuralRadar from the packaged `.exe`, it will automatically detect that it is packaged. 
To prevent writing data to the `dist` or `Program Files` folders, it redirects local data storage to your Windows user profile:

- **Database:** `%LOCALAPPDATA%\NeuralRadar\data\neuralradar.db`
- **Logs:** `%LOCALAPPDATA%\NeuralRadar\logs\neuralradar.log`

*(In development mode via `python app/main.py`, it continues to use the project's root `data/` and `logs/` folders).*

## Troubleshooting
- **Missing modules on run**: If the `.exe` crashes immediately, check `%LOCALAPPDATA%\NeuralRadar\logs\neuralradar.log` for missing dependency errors.
- **Antivirus false positives**: PyInstaller executables are sometimes flagged by Windows Defender. You may need to add an exclusion for the `dist` folder during development.
