# NeuralRadar

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)
*(Badge placeholders)*

> **Network discovery, mapping and monitoring platform by NeuralShield.**

## Description

**NeuralRadar** is a professional network discovery, inventory, and monitoring tool built by NeuralShield. It starts as an advanced IP scanner but is designed to grow into a modular network visibility platform tailored for homelabs, IT admins, developers, and security-focused users.

The initial version focuses on scanning local networks, detecting active devices, and exposing critical details such as IP addresses, hostnames, MAC addresses, vendors, and open ports through a clean, intuitive graphical interface. Users can easily discover unknown devices, identify servers, routers, NAS systems, virtual machines, containers, and workstations, and then save or export the results for further analysis.

NeuralRadar is more than a simple IP scanner. It is a robust, modular network radar that will evolve to include active monitoring, network mapping, service checks, security warnings, and deep integrations with modern virtualization and containerization platforms like Docker, LXC, and Proxmox.

## Key Features

*   **Advanced IP Scanning:** Rapidly discover active hosts on local networks.
*   **Comprehensive Device Profiling:** Identify hostnames, MAC addresses, hardware vendors, and device types.
*   **Port Scanning:** Detect open ports and running services on discovered devices.
*   **Clean Graphical Interface:** A professional, modern GUI built with PySide6 for intuitive navigation and data visualization.
*   **Data Export & Reporting:** Save, export, and manage network scan results.
*   **Cross-Platform Support:** Built to run on both Windows and Linux environments.

## Planned Modules

NeuralRadar is built with a modular architecture to support future expansions:

*   **IPHawk:** Fast and reliable IP discovery and host detection.
*   **PortScope:** Comprehensive port scanning and service identification.
*   **DeviceVault:** Persistent device inventory and asset management.
*   **NetMap:** Visual, interactive network topology mapping.
*   **WatchTower:** Uptime and latency monitoring for critical network assets.
*   **WebPulse:** Website, API, and SSL certificate health checks.
*   **ShieldAudit:** Basic security checks, vulnerability scanning, and misconfiguration alerts.
*   **ContainerRadar:** Overview and monitoring of Docker, LXC, and Proxmox environments.

## Roadmap

*   [ ] **v0.1:** Initial repository setup and core architecture
*   [ ] **v0.2:** Basic GUI layout and component integration
*   [ ] **v0.3:** Local network scanner implementation
*   [ ] **v0.4:** Device inventory and database integration
*   [ ] **v0.5:** Port scanner module
*   [ ] **v1.0:** First stable release

## Installation

*(Installation instructions placeholder - coming soon)*

```bash
# Example placeholder for future installation steps
# git clone https://github.com/NeuralShield/NeuralRadar.git
# cd NeuralRadar
# pip install -r requirements.txt
# python main.py
```

## Usage

*(Usage instructions placeholder - coming soon)*

## Screenshots

*(Screenshots placeholder - coming soon)*

---

## ⚠️ Security and Ethical Usage Notice

**Important:** NeuralRadar is a powerful network discovery and scanning tool. It is intended strictly for use on networks, systems, and devices that you own or have explicit, documented permission to test and monitor. Unauthorized scanning of third-party networks or infrastructure is strictly prohibited and may violate local or international laws. Always ensure you have the necessary authorization before running network scans.

### 🔍 Vendor Detection Note
*   Vendor detection is based on MAC OUI prefixes.
*   Some vendors may still show "Unknown" if the OUI is missing from the local database.
*   Users can add custom mappings in `data/oui.csv`.

## Contributing

We welcome contributions to NeuralRadar!
*(Contribution guidelines placeholder - coming soon)*

## License

*(License information placeholder - coming soon)*

## Credits

**Built by:** NeuralShield  
**Created by:** 0xRootNull  

---
*Built with Python 3.12, PySide6, Scapy, python-nmap, and more.*
