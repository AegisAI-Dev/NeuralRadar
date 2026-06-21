# v0.2-alpha Release Verification Checklist

Run through these steps before finalizing a release build to ensure safety boundaries and operational functionality.

## Development Mode Tests
- [ ] Clean install test using `.venv`
- [ ] Run application (`python app/main.py`)
- [ ] Verify version displays as `v0.2-alpha` in window title and Settings/About
- [ ] Test Dashboard statistics (with and without data)
- [ ] Test Refresh Stats button
- [ ] Test all export buttons (Devices CSV, Devices JSON, Full Inventory JSON)
- [ ] Test report buttons (Markdown and HTML reports)
- [ ] Verify reports contain defensive findings, privacy section, and no offensive language
- [ ] Test all modules (IPHawk, PortScope, WebPulse, DeviceVault)
- [ ] Verify existing DeviceVault edit/save and export functionality still works
- [ ] Verify no local database (`data/neuralradar.db`) is committed to the repository
- [ ] Verify no `logs/` directory or files are committed
- [ ] Verify `requirements.txt` installation works cleanly
- [ ] Verify `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `TESTING.md` are accurate and up-to-date
- [ ] Verify ethical usage and privacy notices are prominently displayed in Settings and README
- [ ] Verify GitHub repository is clean of cache artifacts (`__pycache__`, `.pytest_cache`, etc.)

## Internal Build Tests (Windows)
- [ ] Build Windows executable using `.\scripts\build_windows.ps1`
- [ ] Run packaged app at `dist\NeuralRadar\NeuralRadar.exe`
- [ ] Confirm app starts successfully
- [ ] Confirm Dashboard statistics load
- [ ] Confirm export and report buttons work
- [ ] Confirm Settings/About opens
- [ ] Confirm IPHawk opens and runs
- [ ] Confirm DeviceVault opens
- [ ] Confirm PortScope opens and runs
- [ ] Confirm WebPulse opens and runs
- [ ] Confirm database is created in `%LOCALAPPDATA%\NeuralRadar\data\neuralradar.db` when running packaged exe
- [ ] Confirm logs are created in `%LOCALAPPDATA%\NeuralRadar\logs\neuralradar.log` when running packaged exe
- [ ] Confirm local developer `data/` and `logs/` folders were not bundled inside the PyInstaller distribution

## Release Packaging
- [ ] Create `NeuralRadar-v0.2-alpha-windows-x64.zip` containing the **full** `dist\NeuralRadar\` folder (not just the .exe)
- [ ] Do not include database or log files in the release ZIP
- [ ] Verify no secrets, API keys, or environment data is included in any report/export
- [ ] Verify all reports open correctly in browsers and Markdown editors
- [ ] Verify CSV exports open cleanly in spreadsheet software

All tests must pass before tagging v0.2-alpha release with GitHub Desktop.
