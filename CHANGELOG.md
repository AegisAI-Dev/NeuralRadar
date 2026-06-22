# Changelog

All notable changes to NeuralRadar will be documented in this file.

## v0.3-alpha — Internal Development Checkpoint

**Internal only — no public ZIP, no website update, no public release.**

### DeviceVault
- Advanced search and filters (status, device type, dynamic vendor)
- Saved filter presets with name, search_text, status, device_type, vendor, scope
- Bulk classification (device type and tag updates on selected rows)
- Scoped exports/reports (Full Inventory, Current Filtered View, Selected Devices)
- Inventory hygiene insights (unclassified, missing name/vendor, has services/web, TLS warnings, stale)
- Hygiene quick filters with active state and filter summary integration
- Result count and active filter summary labels
- Multi-row selection with correct ID mapping after sorting/filtering
- Row selection/edit/save preserved after sorting

### IPHawk
- Known devices review from DeviceVault
- Recheck selected known device (single IP only)
- Recheck all known devices (only loaded known IPs)
- Current Status and Change indicators

### PortScope
- Stored services review from DeviceVault
- Recheck selected stored service (single IP/port only)
- Recheck services for selected device (only stored ports for that device)
- Last Known Service State with Current State and Change indicators

### WebPulse
- Stored endpoints review/recheck from DeviceVault
- Recheck selected/all stored endpoints (reuses safe checker)
- Last Known State table with TLS expiry insight and days-until-expiry calculation
- Row selection populates target input without auto-check

### Integration and Safety
- Full internal integration audit passed (Phase 12A)
- All workflows preserve local-only, privacy-safe, defensive-only behavior
- No telemetry, no cloud sync, no external APIs, no exploitation, no brute forcing, no vulnerability scanning, no crawling, no UDP/SYN scanning
- No database schema changes
- All exports/reports strictly local
- py_compile and startup verified across all modules

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
