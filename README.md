# NeuralRadar v0.3-alpha (Internal Development Checkpoint)
## Built by NeuralShield

> **Modular local-first network discovery, inventory and visibility platform.**

NeuralRadar is a privacy-friendly, local-first network visibility tool. It provides modular capabilities for discovery and asset inventory without telemetry or external APIs.

## Current Features (v0.3-alpha Internal Checkpoint)

**Core Modules**
- **IPHawk**: Safe local device discovery with known-device recheck from DeviceVault and status/change indicators
- **DeviceVault**: Persistent local asset inventory (SQLite) with advanced filters/search, saved presets, bulk classification, scoped exports/reports, inventory hygiene insights and quick filters, multi-row selection
- **PortScope**: Safe TCP connect service discovery with stored services review/recheck and last-known/current state with change indicators
- **WebPulse**: Safe HTTP/HTTPS metadata and TLS checks with stored endpoint recheck, Last Known State table, and TLS expiry insight

**Data & Output Features**
- Dashboard inventory statistics (Total Devices, Online, Open Services, Web Endpoints, TLS Warnings, Last Updated)
- DeviceVault CSV and JSON export (with filtering and selected-device scopes)
- Full Inventory JSON export
- Filtered, selected, and full scoped Markdown and HTML reports
- Local self-contained reports with defensive findings and privacy section

**Safety Boundaries**
- Local-only operation (no telemetry, no cloud sync, no external APIs)
- No vulnerability scanning, exploit checks, brute forcing, crawling, or offensive capabilities
- **Only scan systems you own or have explicit permission to test**

## Screenshots
*(Screenshots coming soon - refer to `docs/screenshots/`)*

## Security and Ethical Usage Notice
⚠️ **Only scan networks you own or have permission to test.**

NeuralRadar is strictly a visibility and inventory tool. It does **NOT** include vulnerability scanning, exploit checks, brute forcing, or any offensive capabilities.

## Privacy Statement
NeuralRadar operates entirely locally. There is **NO** telemetry, **NO** cloud sync, and **NO** external APIs. Your network data never leaves your machine. Reports and exports are saved locally only.

## Installation Instructions

### Prerequisites
- Python 3.10+
- Virtual Environment recommended

### Setup
#### Windows
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## How to Run
```bash
python app/main.py
```

## Building for Windows
See `scripts/build_windows.ps1` for PyInstaller one-folder builds. Distribute the full `dist\NeuralRadar\` folder (not just the .exe).

## Roadmap
See [ROADMAP.md](ROADMAP.md) for details on upcoming features (v0.3 public release preparation, further reporting enhancements, etc.).

## Contributing
Contributions are welcome. Please ensure new features align with the core philosophy: local-first, safe, defensive, and no telemetry.

## License
[LICENSE](LICENSE)

## Credits
Built by NeuralShield  
Created by 0xRootNull
