from sqlalchemy.orm import Session
from app.modules.devicevault.models import Device
from app.core.logger import logger
import datetime

class DeviceVaultService:
    @staticmethod
    def get_all_devices(db: Session):
        return db.query(Device).all()

    @staticmethod
    def search_devices(db: Session, query: str):
        q = f"%{query}%"
        return db.query(Device).filter(
            (Device.ip_address.ilike(q)) |
            (Device.name.ilike(q)) |
            (Device.detected_hostname.ilike(q)) |
            (Device.mac_address.ilike(q)) |
            (Device.vendor.ilike(q)) |
            (Device.device_type.ilike(q)) |
            (Device.tags.ilike(q)) |
            (Device.notes.ilike(q))
        ).all()

    @staticmethod
    def update_manual_fields(db: Session, device_id: int, name: str, device_type: str, tags: str, notes: str):
        device = db.query(Device).filter(Device.id == device_id).first()
        if device:
            device.name = name
            device.device_type = device_type
            device.tags = tags
            device.notes = notes
            try:
                db.commit()
                db.refresh(device)
                logger.info(f"Updated manual fields for device {device.ip_address}")
                return True
            except Exception as e:
                db.rollback()
                logger.error(f"Error updating device: {e}")
        return False

    @staticmethod
    def save_scan_results(db: Session, results: list):
        """
        results: List of dictionaries matching the IPHawk host_data format.
        Preserves manual edits (name, device_type, tags, notes) if they differ from default.
        """
        saved_count = 0
        updated_count = 0
        
        for host in results:
            ip = host.get('ip', '')
            mac = host.get('mac', '—')
            if not ip:
                continue

            device = None
            if mac and mac != '—' and mac != 'Pending...':
                device = db.query(Device).filter(Device.mac_address == mac).first()
            if not device:
                device = db.query(Device).filter(Device.ip_address == ip).first()

            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            vendor = host.get('vendor_override', '') or host.get('vendor', '—')
            if vendor == "Unknown": vendor = "—"

            if device:
                device.ip_address = ip
                device.status = "Online"
                device.last_seen = now
                device.response_time = str(host.get('response_time', 0))
                
                # Protect user edits. If existing fields are default "—" or "Unclassified", we can overwrite.
                if device.name == "—" or not device.name:
                    device.name = host.get('display_name', '—')
                    
                device.detected_hostname = host.get('hostname', '—')
                if device.mac_address == "—" or device.mac_address == "Pending...":
                    device.mac_address = mac
                    
                if vendor != "—" and (device.vendor == "—" or not device.vendor):
                    device.vendor = vendor
                    
                if device.device_type == "Unclassified" or not device.device_type:
                    device.device_type = host.get('device_type', 'Unclassified')
                    
                device.discovery_source = host.get('source', '—')
                device.confidence = host.get('confidence', '—')
                
                updated_count += 1
            else:
                new_device = Device(
                    ip_address=ip,
                    name=host.get('display_name', '—'),
                    detected_hostname=host.get('hostname', '—'),
                    mac_address=mac,
                    vendor=vendor,
                    device_type=host.get('device_type', 'Unclassified'),
                    status="Online",
                    tags="",
                    notes=host.get('notes', ''),
                    discovery_source=host.get('source', '—'),
                    confidence=host.get('confidence', '—'),
                    first_seen=now,
                    last_seen=now,
                    response_time=str(host.get('response_time', 0)),
                    source_module="IPHawk"
                )
                db.add(new_device)
                saved_count += 1

        try:
            db.commit()
            if saved_count > 0 or updated_count > 0:
                logger.info(f"DeviceVault sync: {saved_count} new devices, {updated_count} updated.")
            return True, saved_count, updated_count
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving to DeviceVault: {e}")
            return False, 0, 0
