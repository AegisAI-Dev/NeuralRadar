# Release Verification Checklist

Run through these steps before finalizing a release build to ensure safety boundaries and operational functionality.

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
