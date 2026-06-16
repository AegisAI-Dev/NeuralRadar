# NeuralRadar v0.1-alpha
## Built by NeuralShield

> **Modular network discovery, inventory and visibility platform.**

NeuralRadar is a local-first, privacy-friendly network visibility tool. It provides modular capabilities for network discovery and asset inventory without sending telemetry or relying on external APIs.

## Current Features (v0.1-alpha)
- **IPHawk**: Local network discovery
- **DeviceVault**: Local asset inventory using SQLite persistence
- **PortScope**: Safe TCP connect port discovery
- **WebPulse**: Safe HTTP/HTTPS checks
- **Database Persistence**: Stores open ports per device and web metadata per device/service.

## Screenshots
*(Screenshots coming soon - refer to `docs/screenshots/`)*

## Security and Ethical Usage Notice
⚠️ **Only scan networks you own or have permission to test.**
NeuralRadar is strictly a visibility tool. It does NOT include vulnerability scanning, exploit checks, brute forcing, directory busting, payload testing, or any offensive capabilities.

## Privacy Statement
NeuralRadar operates entirely locally. There is NO telemetry, NO cloud sync, and NO external APIs used. Your network data never leaves your machine.

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

## Roadmap
See [ROADMAP.md](ROADMAP.md) for details on upcoming features.

## Contributing
Contributions are welcome. Please ensure new features align with the core philosophy: local-first, safe, and no telemetry. 

## License
[Insert License Here]

## Credits
Built by NeuralShield
Created by 0xRootNull
