"""DeviceVault Export System.
Safe local export of inventory to CSV and JSON.
No cloud, no telemetry, local-only.
"""
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy.orm import Session

from app.modules.devicevault.models import Device, OpenPort, WebService
from app.core.logger import logger
from app.core.version import VERSION


class DeviceVaultExporter:
    """Safe exporter for DeviceVault data to CSV and JSON."""

    @staticmethod
    def _get_session():
        """Get a fresh DB session."""
        from app.core.database import SessionLocal
        return SessionLocal()

    @staticmethod
    def export_devices_csv(output_path: str, device_ids: list = None) -> bool:
        """Export devices to CSV."""
        try:
            db = DeviceVaultExporter._get_session()
            if device_ids:
                devices = db.query(Device).filter(Device.id.in_(device_ids)).all()
            else:
                devices = db.query(Device).all()
            db.close()

            if not devices:
                logger.warning("No devices to export to CSV")
                return False

            fieldnames = [
                "Status", "IP Address", "Name", "Detected Hostname", "MAC Address",
                "Vendor", "Device Type", "Tags", "Notes", "Discovery Source",
                "Confidence", "First Seen", "Last Seen", "Response Time", "Source Module"
            ]

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for device in devices:
                    row = {
                        "Status": device.status or "—",
                        "IP Address": device.ip_address or "—",
                        "Name": device.name or "—",
                        "Detected Hostname": device.detected_hostname or "—",
                        "MAC Address": device.mac_address or "—",
                        "Vendor": device.vendor or "—",
                        "Device Type": device.device_type or "—",
                        "Tags": device.tags or "—",
                        "Notes": (device.notes or "").replace("\n", " ").replace("\r", " "),
                        "Discovery Source": device.discovery_source or "—",
                        "Confidence": device.confidence or "—",
                        "First Seen": device.first_seen or "—",
                        "Last Seen": device.last_seen or "—",
                        "Response Time": device.response_time or "—",
                        "Source Module": device.source_module or "—",
                    }
                    writer.writerow(row)

            logger.info(f"Exported {len(devices)} devices to CSV: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Device CSV export failed: {e}")
            return False

    @staticmethod
    def export_devices_json(output_path: str, device_ids: list = None) -> bool:
        """Export devices to JSON with metadata."""
        try:
            db = DeviceVaultExporter._get_session()
            if device_ids:
                devices = db.query(Device).filter(Device.id.in_(device_ids)).all()
            else:
                devices = db.query(Device).all()
            db.close()

            if not devices:
                logger.warning("No devices to export to JSON")
                return False

            records = []
            for device in devices:
                records.append({
                    "status": device.status or "—",
                    "ip_address": device.ip_address or "—",
                    "name": device.name or "—",
                    "detected_hostname": device.detected_hostname or "—",
                    "mac_address": device.mac_address or "—",
                    "vendor": device.vendor or "—",
                    "device_type": device.device_type or "—",
                    "tags": device.tags or "",
                    "notes": device.notes or "",
                    "discovery_source": device.discovery_source or "—",
                    "confidence": device.confidence or "—",
                    "first_seen": device.first_seen or "—",
                    "last_seen": device.last_seen or "—",
                    "response_time": device.response_time or "—",
                    "source_module": device.source_module or "—",
                })

            data = {
                "exported_at": datetime.now().isoformat(),
                "app_name": "NeuralRadar",
                "app_version": VERSION,
                "export_type": "devices",
                "total_records": len(records),
                "records": records
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Exported {len(records)} devices to JSON: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Device JSON export failed: {e}")
            return False

    @staticmethod
    def export_services_csv(output_path: str) -> bool:
        """Export open services to CSV."""
        try:
            db = DeviceVaultExporter._get_session()
            services = db.query(OpenPort).all()
            db.close()

            if not services:
                logger.warning("No services to export to CSV")
                return False

            fieldnames = [
                "Device IP", "Device Name", "Port", "Protocol", "Service Guess",
                "State", "Response Time", "First Seen", "Last Seen", "Source Module"
            ]

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for service in services:
                    row = {
                        "Device IP": service.ip_address or "—",
                        "Device Name": "—",  # Would need join for full name
                        "Port": service.port or "—",
                        "Protocol": service.protocol or "—",
                        "Service Guess": service.service_guess or "—",
                        "State": service.state or "—",
                        "Response Time": service.response_time or "—",
                        "First Seen": service.first_seen or "—",
                        "Last Seen": service.last_seen or "—",
                        "Source Module": service.source_module or "—",
                    }
                    writer.writerow(row)

            logger.info(f"Exported {len(services)} services to CSV: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Services CSV export failed: {e}")
            return False

    @staticmethod
    def export_web_metadata_csv(output_path: str) -> bool:
        """Export web metadata to CSV."""
        try:
            db = DeviceVaultExporter._get_session()
            web_services = db.query(WebService).all()
            db.close()

            if not web_services:
                logger.warning("No web metadata to export to CSV")
                return False

            fieldnames = [
                "Device IP", "Device Name", "URL", "Scheme", "Host", "Port", "Status",
                "HTTP Code", "Reason", "Final URL", "Redirect Count", "Page Title",
                "Server Header", "Content Type", "SSL Enabled", "SSL Expiry",
                "SSL Issuer", "TLS Status", "Error Message", "Response Time",
                "First Seen", "Last Checked", "Source Module"
            ]

            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                writer.writeheader()
                for ws in web_services:
                    row = {
                        "Device IP": ws.ip_address or "—",
                        "Device Name": "—",
                        "URL": ws.url or "—",
                        "Scheme": ws.scheme or "—",
                        "Host": ws.host or "—",
                        "Port": ws.port or "—",
                        "Status": ws.status or "—",
                        "HTTP Code": ws.http_code or "—",
                        "Reason": ws.reason or "—",
                        "Final URL": ws.final_url or "—",
                        "Redirect Count": ws.redirect_count or "0",
                        "Page Title": (ws.page_title or "—").replace("\n", " "),
                        "Server Header": ws.server_header or "—",
                        "Content Type": ws.content_type or "—",
                        "SSL Enabled": ws.ssl_enabled or "—",
                        "SSL Expiry": ws.ssl_expiry or "—",
                        "SSL Issuer": ws.ssl_issuer or "—",
                        "TLS Status": "—",  # Derived if needed
                        "Error Message": ws.error_message or "—",
                        "Response Time": ws.response_time or "—",
                        "First Seen": ws.first_seen or "—",
                        "Last Checked": ws.last_checked or "—",
                        "Source Module": ws.source_module or "—",
                    }
                    writer.writerow(row)

            logger.info(f"Exported {len(web_services)} web records to CSV: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Web metadata CSV export failed: {e}")
            return False

    @staticmethod
    def export_full_inventory_json(output_path: str, device_ids: list = None) -> bool:
        """Export full inventory (devices, services, web metadata) as JSON with metadata."""
        try:
            db = DeviceVaultExporter._get_session()
            if device_ids:
                devices = db.query(Device).filter(Device.id.in_(device_ids)).all()
            else:
                devices = db.query(Device).all()
            services = db.query(OpenPort).all()
            web_services = db.query(WebService).all()
            db.close()

            if not devices and not services and not web_services:
                logger.warning("No data to export to full inventory JSON")
                return False

            # Convert to dicts
            device_list = [ {
                "id": d.id,
                "ip_address": d.ip_address,
                "name": d.name,
                "detected_hostname": d.detected_hostname,
                "mac_address": d.mac_address,
                "vendor": d.vendor,
                "device_type": d.device_type,
                "status": d.status,
                "tags": d.tags,
                "notes": d.notes,
                "discovery_source": d.discovery_source,
                "confidence": d.confidence,
                "first_seen": d.first_seen,
                "last_seen": d.last_seen,
                "response_time": d.response_time,
                "source_module": d.source_module,
            } for d in devices ]

            service_list = [ {
                "device_id": s.device_id,
                "ip_address": s.ip_address,
                "port": s.port,
                "protocol": s.protocol,
                "service_guess": s.service_guess,
                "state": s.state,
                "response_time": s.response_time,
                "first_seen": s.first_seen,
                "last_seen": s.last_seen,
                "source_module": s.source_module,
            } for s in services ]

            web_list = [ {
                "device_id": w.device_id,
                "ip_address": w.ip_address,
                "url": w.url,
                "scheme": w.scheme,
                "host": w.host,
                "port": w.port,
                "status": w.status,
                "http_code": w.http_code,
                "reason": w.reason,
                "final_url": w.final_url,
                "redirect_count": w.redirect_count,
                "page_title": w.page_title,
                "server_header": w.server_header,
                "content_type": w.content_type,
                "ssl_enabled": w.ssl_enabled,
                "ssl_expiry": w.ssl_expiry,
                "ssl_issuer": w.ssl_issuer,
                "error_message": w.error_message,
                "response_time": w.response_time,
                "first_seen": w.first_seen,
                "last_checked": w.last_checked,
                "source_module": w.source_module,
            } for w in web_services ]

            data = {
                "exported_at": datetime.now().isoformat(),
                "app_name": "NeuralRadar",
                "app_version": VERSION,
                "export_type": "full_inventory",
                "total_devices": len(device_list),
                "total_services": len(service_list),
                "total_web_records": len(web_list),
                "devices": device_list,
                "services": service_list,
                "web_metadata": web_list
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            total = len(device_list) + len(service_list) + len(web_list)
            logger.info(f"Exported full inventory ({total} records) to JSON: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Full inventory JSON export failed: {e}")
            return False


# Convenience functions for GUI
def export_devices_csv(output_path: str, device_ids: list = None) -> bool:
    return DeviceVaultExporter.export_devices_csv(output_path, device_ids)


def export_devices_json(output_path: str, device_ids: list = None) -> bool:
    return DeviceVaultExporter.export_devices_json(output_path, device_ids)


def export_full_inventory_json(output_path: str, device_ids: list = None) -> bool:
    return DeviceVaultExporter.export_full_inventory_json(output_path, device_ids)


def export_services_csv(output_path: str) -> bool:
    return DeviceVaultExporter.export_services_csv(output_path)


def export_web_metadata_csv(output_path: str) -> bool:
    return DeviceVaultExporter.export_web_metadata_csv(output_path)
