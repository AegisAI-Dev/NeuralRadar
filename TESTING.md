# NeuralRadar v0.3-alpha Internal Testing Checklist

**This is an INTERNAL checkpoint only. No public ZIP. No website update.**

Use this checklist to perform manual quality assurance for the v0.3 internal state.

## v0.3 Internal Regression (Phase 12A Verified)
- [ ] DeviceVault workflows (filters, presets, bulk, hygiene, quick filters, scoped exports/reports, multi-select, row mapping after sorting)
- [ ] IPHawk workflows (known devices load/recheck, status/change indicators, single-IP recheck only)
- [ ] PortScope workflows (stored services load/recheck, last-known/current state, change indicators, targeted recheck only)
- [ ] WebPulse workflows (stored endpoints load/recheck, Last Known State table, TLS expiry insight, row selection without auto-check)
- [ ] Dashboard stats and Refresh Stats
- [ ] All export/report scopes (Full, Filtered, Selected) and Markdown/HTML reports
- [ ] DeviceVault service helpers (get_stored_*, get_known_devices_summary)
- [ ] Safety boundaries (no telemetry, no cloud, no offensive capabilities, local-only)
- [ ] py_compile on all core files
- [ ] python app/main.py (successful startup and navigation)
- [ ] Full navigation (Dashboard, IPHawk, DeviceVault, PortScope, WebPulse, Settings)

All v0.3 internal tests must pass before any public release consideration. v0.2-alpha remains the latest public release reference.

## Core Setup
- [ ] Virtual environment setup
- [ ] Requirements install
- [ ] App startup with v0.3-alpha version in title

## General
- [ ] No telemetry: Verify no network traffic to external services
- [ ] Local-only: All exports/reports saved locally
- [ ] Logging: Check logs for success/failure
- [ ] No secrets: No environment data in reports/exports

v0.3 is internal development checkpoint only. No public release artifacts created.
