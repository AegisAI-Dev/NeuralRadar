# Changelog

All notable changes to NeuralRadar will be documented in this file.

## v0.3-alpha (Internal Development Checkpoint)

### Internal Checkpoint
- DeviceVault filters, search, and scope selector
- Filtered exports and reports
- Result count and filter summary display
- Sortable DeviceVault table
- **Internal only**: No public ZIP release, no website updates

## v0.2-alpha

### Added
- DeviceVault CSV/JSON export system
- Full Inventory JSON export
- Dashboard inventory statistics (Total Devices, Online, Open Services, Web Endpoints, TLS Warnings, Last Updated)
- Refresh Stats button on dashboard
- Local Markdown report generator
- Local self-contained HTML report generator
- Defensive findings/notes section in reports (informational only, no exploit guidance)
- Preserved local-only/privacy-safe behavior throughout
- Stability fixes for GUI theme compatibility

### Security
- Local-only operation enforced
- No telemetry or external analytics
- No vulnerability scanning or exploit checks
- No cloud sync or crawling
- Reports and exports are strictly local files

## [v0.1-alpha] - Initial Release

### Added
- Initial PySide6 GUI framework.
- **IPHawk**: Local network discovery.
- **DeviceVault**: Persistent asset inventory.
- **PortScope**: Safe TCP connect port discovery.
- **WebPulse**: Safe HTTP/HTTPS checks and TLS evaluation.
- SQLite persistence engine.
- Open service persistence in DeviceVault.
- Web metadata persistence in DeviceVault.

### Security
- Local-only operation enforced.
- No telemetry or external analytics.
- Safe TCP connect checks only.
- No vulnerability scanning.
- No exploit checks included.
