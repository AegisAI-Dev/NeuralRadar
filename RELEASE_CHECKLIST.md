# Release Verification Checklist

Run through these steps before finalizing a release build to ensure safety boundaries and operational functionality.

## Development Mode Tests
- [ ] Clean install test using `.venv`
- [ ] Run application (`python app/main.py`)
- [ ] Test all modules (IPHawk, PortScope, WebPulse, DeviceVault)
- [ ] Verify no local database (`data/neuralradar.db`) is committed to the repository
- [ ] Verify no `logs/` directory or files are committed
- [ ] Verify `requirements.txt` installation works cleanly
- [ ] Verify `README.md` is accurate and up-to-date
- [ ] Verify version displays as `v0.1-alpha` in GUI
- [ ] Verify GitHub repository is clean of cache artifacts (`__pycache__`, `.pytest_cache`, etc.)
- [ ] Verify ethical usage and privacy notices are prominently displayed in Settings and README

## Internal Build Tests (Windows)
- [ ] Build Windows executable using `.\scripts\build_windows.ps1`
- [ ] Run packaged app at `dist\NeuralRadar\NeuralRadar.exe`
- [ ] Confirm app starts successfully
- [ ] Confirm Settings/About opens
- [ ] Confirm IPHawk opens and runs
- [ ] Confirm DeviceVault opens
- [ ] Confirm PortScope opens and runs
- [ ] Confirm WebPulse opens and runs
- [ ] Confirm database is created in `%LOCALAPPDATA%\NeuralRadar\data\neuralradar.db` when running packaged exe
- [ ] Confirm logs are created in `%LOCALAPPDATA%\NeuralRadar\logs\neuralradar.log` when running packaged exe
- [ ] Confirm local developer `data/` and `logs/` folders were not bundled inside the PyInstaller distribution
