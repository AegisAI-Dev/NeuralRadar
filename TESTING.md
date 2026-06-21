# NeuralRadar v0.3-alpha Internal Development Checkpoint Manual Testing Checklist

## v0.3-alpha Internal Tests (Filters & UI)
- [ ] **DeviceVault filters and search**: Test text search, scope selector (All Devices, Online Only, etc.), verify results update dynamically.
- [ ] **Sortable table**: Click column headers (IP, Status, Services, etc.), verify ascending/descending sort.
- [ ] **Result count and filter summary**: Verify "Showing X of Y results" updates with filters/search.
- [ ] **Filtered exports/reports**: Apply filter, export or generate report, verify only filtered results are included.
- [ ] **Scope selector persistence**: Change scope, verify it remembers on page reload or navigation.

## v0.2-alpha Manual Testing Checklist
Use this checklist to perform manual quality assurance before finalizing a release build.

## Core Setup
- [ ] **Virtual environment setup**: Verify `venv` creation and activation works correctly across Windows and Linux.
- [ ] **Requirements install**: Ensure `pip install -r requirements.txt` succeeds and pulls necessary packages (`PySide6`, `loguru`, `SQLAlchemy`).
- [ ] **App startup**: Run `python app/main.py`. The GUI should launch without console errors, and the window title should display `NeuralRadar v0.3-alpha`.
- [ ] **Version check**: Confirm app/core/version.py is v0.3-alpha.

## Dashboard
- [ ] **Dashboard opens**: Verify hero section, safety strip, module cards, and new inventory statistics row are visible.
- [ ] **Dashboard statistics**: Confirm Total Devices, Online, Open Services, Web Endpoints, TLS Warnings, and Last Updated display correctly from existing DeviceVault data.
- [ ] **Refresh Stats button**: Click Refresh Stats. Values should update (or show 0/— for empty database).
- [ ] **Empty database behavior**: With an empty DeviceVault, stats should show 0 values and "—" for Last Updated.

## DeviceVault Export & Reporting
- [ ] **Export Devices CSV**: Click button, choose location. Verify CSV is valid and opens in Excel/LibreOffice with correct columns.
- [ ] **Export Devices JSON**: Verify JSON is pretty-formatted with metadata and correct records.
- [ ] **Full Inventory JSON**: Verify JSON contains devices, services, and web_metadata sections with metadata.
- [ ] **Generate Markdown Report**: Verify .md file contains header, executive summary (using stats), device/services/web tables, defensive findings, and privacy section.
- [ ] **Generate HTML Report**: Verify self-contained .html file opens in browser with dark cyber-tech styling, all sections, and safe escaping.
- [ ] **Empty database report/export**: Verify clean "No data available" message for reports and exports.

## Core Modules Regression
- [ ] **IPHawk**: Run scan, save results to DeviceVault. Verify devices appear.
- [ ] **DeviceVault**: View devices, edit manual fields, save. Verify persistence after restart. Test new filters, search, sorting.
- [ ] **PortScope**: Scan from DeviceVault, save open services. Verify they attach to devices.
- [ ] **WebPulse**: Run checks, save metadata. Verify TLS warnings and web records appear in stats/reports.
- [ ] **Navigation**: Switch between all pages (Dashboard, IPHawk, DeviceVault, PortScope, WebPulse, Settings). Verify no crashes.

## Packaged Build
- [ ] **Build**: Run `.\\scripts\\build_windows.ps1`.
- [ ] **Packaged exe**: Run `dist\\NeuralRadar\\NeuralRadar.exe`. Verify all features work (stats, export, reports, filters).
- [ ] **Internal Checkpoint**: No public ZIP created. No website update.

## General
- [ ] **No telemetry**: Verify no network traffic to external services during normal operation.
- [ ] **Local-only**: All exports/reports saved locally via user-selected paths.
- [ ] **Logging**: Check logs for export/report success/failure messages.
- [ ] **No secrets**: Exported reports do not contain environment variables, API keys, or system paths.

All tests must pass before marking v0.3-alpha internal checkpoint complete. This is an internal development checkpoint only — no public release.
