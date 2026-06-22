# v0.3-alpha Internal Development Checkpoint Verification Checklist

**This is an INTERNAL checkpoint only. No public ZIP release. No website update. No public artifacts generated.**

Run through these steps to confirm the v0.3 internal state is stable.

## Development Mode Tests
- [ ] Clean install test using `.venv`
- [ ] Run application (`python app/main.py`)
- [ ] Verify version displays as `v0.3-alpha` in window title and Settings/About
- [ ] Test all DeviceVault workflows (filters, presets, bulk, hygiene, scoped exports/reports)
- [ ] Test IPHawk known-device recheck and indicators
- [ ] Test PortScope stored-service recheck and state indicators
- [ ] Test WebPulse stored-endpoint recheck and Last Known State
- [ ] Test Dashboard statistics and Refresh Stats
- [ ] Test all export/report scopes (Full, Filtered, Selected) and reports
- [ ] Verify all service helpers (get_stored_*, get_known_devices_summary)
- [ ] Verify no local database or logs are committed
- [ ] Verify `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `TESTING.md`, `RELEASE_CHECKLIST.md` accurately reflect internal v0.3 state
- [ ] Verify ethical usage and privacy notices are displayed
- [ ] Verify no cache artifacts

## Internal Build Tests (Windows)
- [ ] Build using scripts if testing (not required for internal checkpoint)
- [ ] Run packaged app and confirm all v0.3 features work
- [ ] Confirm no public release ZIP created
- [ ] Confirm no website update performed

## Internal Checkpoint Notes
- v0.3-alpha is **internal development checkpoint only**
- No public ZIP created
- No website update
- No public release
- All changes local-only, privacy-safe, defensive visibility only
- Full integration audit (Phase 12A) passed with no remaining issues
- v0.2-alpha remains the reference for any public release materials until v0.3 public preparation

All tests must pass before considering any public v0.3 release. Use GitHub Desktop for any repo updates. This is not a public release.
