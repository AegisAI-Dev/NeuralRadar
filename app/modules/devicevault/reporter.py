"""Local Inventory Report Generator for DeviceVault.
Generates self-contained Markdown and HTML reports from existing data only.
No external calls, no telemetry, local-only.
"""
import html
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.modules.devicevault.models import Device, OpenPort, WebService
from app.modules.devicevault.service import DeviceVaultService
from app.core.logger import logger
from app.core.version import VERSION


class DeviceVaultReporter:
    """Generates defensive, local-only inventory reports."""

    @staticmethod
    def _get_session():
        from app.core.database import SessionLocal
        return SessionLocal()

    @staticmethod
    def _generate_header(scope_label: str = "Full Inventory") -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""# NeuralRadar Local Inventory Report

**Built by NeuralShield**  
**Created by 0xRootNull**  
**Version:** {VERSION}  
**Generated:** {now}  
**Report Type:** Local Inventory Report — {scope_label}

> This report is generated from locally stored DeviceVault data. No data was sent externally.

---

"""

    @staticmethod
    def _generate_summary(stats: Dict[str, Any]) -> str:
        return f"""## Executive Summary

| Metric | Value |
|--------|-------|
| Total Devices | {stats.get('total_devices', 0)} |
| Online Devices | {stats.get('online_devices', 0)} |
| Open Services | {stats.get('open_services', 0)} |
| Web Endpoints | {stats.get('web_endpoints', 0)} |
| TLS Warnings | {stats.get('tls_warnings', 0)} |
| Last Updated | {stats.get('last_updated', '—')} |

---

"""

    @staticmethod
    def _generate_devices_section(devices) -> str:
        if not devices:
            return "## Device Inventory\n\nNo devices in inventory.\n\n---\n\n"
        
        md = "## Device Inventory\n\n"
        md += "| Status | IP Address | Name | Hostname | MAC | Vendor | Type | First Seen | Last Seen |\n"
        md += "|--------|------------|------|----------|-----|--------|------|------------|-----------|\n"
        
        for d in devices:
            md += f"| {d.status or '—'} | {d.ip_address or '—'} | {d.name or '—'} | {d.detected_hostname or '—'} | {d.mac_address or '—'} | {d.vendor or '—'} | {d.device_type or '—'} | {d.first_seen or '—'} | {d.last_seen or '—'} |\n"
        
        md += "\n---\n\n"
        return md

    @staticmethod
    def _generate_services_section(services) -> str:
        if not services:
            return "## Open Services\n\nNo open services recorded.\n\n---\n\n"
        
        md = "## Open Services\n\n"
        md += "| Device IP | Port | Protocol | Service | State | Last Seen |\n"
        md += "|-----------|------|----------|---------|-------|-----------|\n"
        
        for s in services:
            md += f"| {s.ip_address or '—'} | {s.port or '—'} | {s.protocol or '—'} | {s.service_guess or '—'} | {s.state or '—'} | {s.last_seen or '—'} |\n"
        
        md += "\n---\n\n"
        return md

    @staticmethod
    def _generate_web_section(web_services) -> str:
        if not web_services:
            return "## Web Metadata\n\nNo web metadata recorded.\n\n---\n\n"
        
        md = "## Web Metadata\n\n"
        md += "| Device IP | URL | Status | HTTP Code | Title | Server | TLS Status | Last Checked |\n"
        md += "|-----------|-----|--------|-----------|-------|--------|------------|--------------|\n"
        
        for w in web_services:
            md += f"| {w.ip_address or '—'} | {w.url or '—'} | {w.status or '—'} | {w.http_code or '—'} | {w.page_title or '—'} | {w.server_header or '—'} | {w.status or '—'} | {w.last_checked or '—'} |\n"
        
        md += "\n---\n\n"
        return md

    @staticmethod
    def _generate_findings(stats: Dict[str, Any]) -> str:
        findings = ["## Findings & Notes\n"]
        findings.append("All information is derived from locally stored DeviceVault data only.\n")
        
        tls = stats.get('tls_warnings', 0)
        if tls > 0:
            findings.append(f"- **TLS Warnings:** {tls} endpoint(s) have TLS-related notes. Review manually.")
        else:
            findings.append("- No TLS warnings recorded.")
        
        findings.append("\n- Device names/types are for inventory hygiene only.")
        findings.append("- Open services and web metadata are informational.")
        findings.append("- No vulnerability scanning or exploitation is performed by NeuralRadar.\n")
        findings.append("---\n\n")
        return "\n".join(findings)

    @staticmethod
    def _generate_privacy_section() -> str:
        return """## Privacy & Limitations

* This report is generated entirely locally from your DeviceVault SQLite database.
* No telemetry, no cloud sync, no external API calls.
* No crawling, no brute forcing, no exploit checks.
* Results depend entirely on what has been previously discovered and saved.
* This report does not constitute a security audit or vulnerability assessment.

**Only scan systems you own or have explicit permission to test.**

---

**Report generated by NeuralRadar v""" + VERSION + """**
"""

    @staticmethod
    def generate_markdown_report(output_path: str, device_ids: list = None, scope_label: str = "Full Inventory") -> bool:
        """Generate a clean Markdown inventory report."""
        try:
            db = DeviceVaultReporter._get_session()
            stats = DeviceVaultService.get_inventory_stats(db)
            devices = db.query(Device).all()
            services = db.query(OpenPort).all()
            web_services = db.query(WebService).all()
            db.close()

            report = (
                DeviceVaultReporter._generate_header() +
                DeviceVaultReporter._generate_summary(stats) +
                DeviceVaultReporter._generate_devices_section(devices) +
                DeviceVaultReporter._generate_services_section(services) +
                DeviceVaultReporter._generate_web_section(web_services) +
                DeviceVaultReporter._generate_findings(stats) +
                DeviceVaultReporter._generate_privacy_section()
            )

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)

            logger.info(f"Markdown report generated: {output_path} ({len(devices)} devices, {len(services)} services, {len(web_services)} web records)")
            return True
        except Exception as e:
            logger.error(f"Markdown report generation failed: {e}")
            return False

    @staticmethod
    def generate_html_report(output_path: str, device_ids: list = None, scope_label: str = "Full Inventory") -> bool:
        """Generate a self-contained HTML report with dark cyber-tech styling."""
        try:
            db = DeviceVaultReporter._get_session()
            stats = DeviceVaultService.get_inventory_stats(db)
            devices = db.query(Device).all()
            services = db.query(OpenPort).all()
            web_services = db.query(WebService).all()
            db.close()

            # Simple self-contained HTML with inline CSS
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>NeuralRadar Local Inventory Report</title>
    <style>
        body {{ font-family: system-ui, -apple-system, sans-serif; background: #050A14; color: #E5E7EB; margin: 0; padding: 40px; line-height: 1.6; }}
        .header {{ background: #0B1020; padding: 30px; border-radius: 12px; border: 1px solid #26364F; margin-bottom: 30px; }}
        h1 {{ color: #00E5FF; margin: 0 0 10px 0; }}
        .meta {{ color: #94A3B8; font-size: 14px; }}
        .section {{ background: #111827; padding: 24px; border-radius: 10px; margin-bottom: 30px; border: 1px solid #26364F; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #26364F; }}
        th {{ background: #0F172A; color: #00E5FF; }}
        .warning {{ color: #FACC15; }}
        .success {{ color: #22C55E; }}
        .footer {{ font-size: 12px; color: #64748B; text-align: center; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>NeuralRadar</h1>
        <div class="meta">Local Inventory Report • Generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        <div class="meta">NeuralShield • v{VERSION} • Created by 0xRootNull</div>
    </div>

    <div class="section">
        <h2>Executive Summary</h2>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Devices</td><td>{stats.get("total_devices", 0)}</td></tr>
            <tr><td>Online Devices</td><td>{stats.get("online_devices", 0)}</td></tr>
            <tr><td>Open Services</td><td>{stats.get("open_services", 0)}</td></tr>
            <tr><td>Web Endpoints</td><td>{stats.get("web_endpoints", 0)}</td></tr>
            <tr><td>TLS Warnings</td><td class="warning">{stats.get("tls_warnings", 0)}</td></tr>
            <tr><td>Last Updated</td><td>{stats.get("last_updated", "—")}</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>Device Inventory</h2>
        <table>
            <tr><th>Status</th><th>IP</th><th>Name</th><th>Hostname</th><th>MAC</th><th>Vendor</th><th>Type</th><th>First Seen</th><th>Last Seen</th></tr>
"""
            for d in devices:
                html_content += f"""            <tr>
                <td>{html.escape(str(d.status or "—"))}</td>
                <td>{html.escape(str(d.ip_address or "—"))}</td>
                <td>{html.escape(str(d.name or "—"))}</td>
                <td>{html.escape(str(d.detected_hostname or "—"))}</td>
                <td>{html.escape(str(d.mac_address or "—"))}</td>
                <td>{html.escape(str(d.vendor or "—"))}</td>
                <td>{html.escape(str(d.device_type or "—"))}</td>
                <td>{html.escape(str(d.first_seen or "—"))}</td>
                <td>{html.escape(str(d.last_seen or "—"))}</td>
            </tr>
"""
            html_content += """        </table>
    </div>

    <div class="section">
        <h2>Open Services</h2>
        <table>
            <tr><th>Device IP</th><th>Port</th><th>Protocol</th><th>Service</th><th>State</th><th>Last Seen</th></tr>
"""
            for s in services:
                html_content += f"""            <tr>
                <td>{html.escape(str(s.ip_address or "—"))}</td>
                <td>{html.escape(str(s.port or "—"))}</td>
                <td>{html.escape(str(s.protocol or "—"))}</td>
                <td>{html.escape(str(s.service_guess or "—"))}</td>
                <td>{html.escape(str(s.state or "—"))}</td>
                <td>{html.escape(str(s.last_seen or "—"))}</td>
            </tr>
"""
            html_content += """        </table>
    </div>

    <div class="section">
        <h2>Web Metadata</h2>
        <table>
            <tr><th>Device IP</th><th>URL</th><th>Status</th><th>HTTP Code</th><th>Title</th><th>Server</th><th>TLS Status</th><th>Last Checked</th></tr>
"""
            for w in web_services:
                html_content += f"""            <tr>
                <td>{html.escape(str(w.ip_address or "—"))}</td>
                <td>{html.escape(str(w.url or "—"))}</td>
                <td>{html.escape(str(w.status or "—"))}</td>
                <td>{html.escape(str(w.http_code or "—"))}</td>
                <td>{html.escape(str(w.page_title or "—"))}</td>
                <td>{html.escape(str(w.server_header or "—"))}</td>
                <td>{html.escape(str(w.status or "—"))}</td>
                <td>{html.escape(str(w.last_checked or "—"))}</td>
            </tr>
"""
            html_content += """        </table>
    </div>

    <div class="section">
        <h2>Findings & Notes</h2>
        <p>All information is derived from locally stored DeviceVault data only. No vulnerability scanning or exploitation is performed.</p>
        <p>TLS warnings are informational only. Review certificates manually. Open services and web metadata are for inventory purposes.</p>
        <p>Devices without names or types are listed for inventory hygiene.</p>
    </div>

    <div class="section">
        <h2>Privacy & Limitations</h2>
        <p>This report is generated entirely locally. No telemetry, no cloud sync, no external API calls, no crawling, no brute forcing.</p>
        <p><strong>Only scan systems you own or have explicit permission to test.</strong></p>
        <p>Results depend entirely on what has been previously discovered and saved in DeviceVault.</p>
    </div>

    <div class="footer">
        Report generated by NeuralRadar v{VERSION} • Local-only • {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
</body>
</html>
"""

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"HTML report generated: {output_path}")
            return True
        except Exception as e:
            logger.error(f"HTML report generation failed: {e}")
            return False


# Convenience functions for GUI
def generate_markdown_report(output_path: str, device_ids: list = None, scope_label: str = "Full Inventory") -> bool:
    return DeviceVaultReporter.generate_markdown_report(output_path)


def generate_html_report(output_path: str, device_ids: list = None, scope_label: str = "Full Inventory") -> bool:
    return DeviceVaultReporter.generate_html_report(output_path)
