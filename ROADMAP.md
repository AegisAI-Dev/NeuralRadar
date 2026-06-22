# NeuralRadar Roadmap

## Completed in v0.3-alpha (Internal Checkpoint)
- DeviceVault advanced filters/search/presets/bulk/hygiene/quick filters/scoped exports/reports
- IPHawk known devices recheck with status/change indicators
- PortScope stored services recheck with last-known/current state and change indicators
- WebPulse stored endpoints recheck with Last Known State table and TLS expiry insight
- Full internal integration audit (Phase 12A)
- All local-only, privacy-safe, defensive-only behavior preserved
- No database schema changes
- No telemetry, no cloud, no offensive capabilities

## Completed in v0.2-alpha
- DeviceVault CSV/JSON export system
- Full Inventory JSON export
- Dashboard inventory statistics (Total Devices, Online Devices, Open Services, Web Endpoints, TLS Warnings, Last Updated)
- Refresh Stats button on dashboard
- Local Markdown report generator
- Local self-contained HTML report generator
- Defensive findings/notes section in reports (informational only)
- Stability fixes for GUI theme compatibility

## Completed in v0.1-alpha
- IPHawk (safe local device discovery)
- DeviceVault (persistent local asset inventory with SQLite)
- PortScope (safe TCP connect service discovery)
- WebPulse (safe HTTP/HTTPS metadata and TLS checks)
- Local-only operation with no telemetry

## Upcoming for Public v0.3 Release
- Final stabilization and testing
- Installer improvements
- Signed releases
- Public documentation and website update
- Optional PDF reports
- Network map visualization (NetMap)
- WatchTower uptime monitoring
- Improved service classification and OUI database

**Core Philosophy Reminder**: Local-first, privacy-safe, defensive visibility only. No offensive capabilities, no telemetry, no cloud sync. v0.3 remains internal until full audit and public release preparation is complete.
