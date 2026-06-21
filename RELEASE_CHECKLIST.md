# v0.3-alpha Internal Development Checkpoint Verification Checklist

**This is an INTERNAL checkpoint only. No public ZIP release. No website update.**

Run through these steps before finalizing the internal v0.3-alpha checkpoint to ensure safety boundaries and operational functionality.

## Development Mode Tests
- [ ] Clean install test using `.venv`
- [ ] Run application (`python app/main.py`)
- [ ] Verify version displays as `v0.3-alpha` in window title and Settings/About (from app/core/version.py)
- [ ] Test DeviceVault filters, search, scope selector
- [ ] Test sortable table columns
- [ ] Test result count and filter summary display
- [ ] Test filtered exports and reports (verify only matching items exported)
- [ ] Test Dashboard statistics and all prior v0.2 features
- [ ] Test all modules (IPHawk, PortScope, WebPulse, DeviceVault)
- [ ] Verify existing DeviceVault edit/save and export functionality still works
- [ ] Verify no local database (`data/neuralradar.db`) is committed to the repository
- [ ] Verify no `logs/` directory or files are committed
- [ ] Verify `requirements.txt` installation works cleanly
- [ ] Verify `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `TESTING.md`, `RELEASE_CHECKLIST.md` are accurate and up-to-date for v0.3-alpha internal checkpoint
- [ ] Verify ethical usage and privacy notices are prominently displayed in Settings and README
- [ ] Verify GitHub repository is clean of cache artifacts (`__pycache__`, `.pytest_cache`, etc.) **(using GitHub Desktop)**

## Internal Build Tests (Windows)
- [ ] Build Windows executable using `.\\scripts\\build_windows.ps1` (if testing build)
- [ ] Run packaged app at `dist\\NeuralRadar\\NeuralRadar.exe`
- [ ] Confirm app starts successfully with v0.3-alpha
- [ ] Confirm DeviceVault filters, sorting, summaries work in packaged build
- [ ] Confirm no public release artifacts created

## Internal Checkpoint Notes
- **No public ZIP** created for v0.3-alpha
- **No website update**
- This marks completion of DeviceVault filters/search/scope, sortable table, filtered outputs, result summaries as internal checkpoint
- All changes limited to allowed files only: app/core/version.py, CHANGELOG.md, README.md, ROADMAP.md, TESTING.md, RELEASE_CHECKLIST.md
- No changes to scanner logic, database schema, build scripts, DeviceVault GUI code (except if syntax error), or any other modules

All tests must pass before considering the v0.3-alpha Internal Development Checkpoint complete. Use GitHub Desktop for any repo updates. This is not a public release.
