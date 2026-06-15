from sqlalchemy.orm import Session
from app.modules.devicevault.models import Device, OpenPort, WebService
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

    @staticmethod
    def get_device_services(db: Session, device_id: int):
        return db.query(OpenPort).filter(OpenPort.device_id == device_id).all()

    @staticmethod
    def save_port_scan_results(db: Session, results: list):
        """
        results: List of dictionaries matching the PortScope result format.
        """
        saved_count = 0
        updated_count = 0
        
        for port_data in results:
            ip = port_data.get('ip', '')
            port_num = port_data.get('port')
            if not ip or not port_num:
                continue

            device = db.query(Device).filter(Device.ip_address == ip).first()
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create stub device if it doesn't exist
            if not device:
                device = Device(
                    ip_address=ip,
                    name="—",
                    detected_hostname="—",
                    mac_address="—",
                    vendor="—",
                    device_type="Unclassified",
                    status="Online",
                    tags="",
                    notes="",
                    discovery_source="—",
                    confidence="—",
                    first_seen=now,
                    last_seen=now,
                    response_time="0",
                    source_module="PortScope"
                )
                db.add(device)
                db.flush() # flush to get device.id
                
            # Check if this port entry already exists for this device
            open_port = db.query(OpenPort).filter(
                OpenPort.device_id == device.id,
                OpenPort.port == port_num,
                OpenPort.protocol == port_data.get('protocol', 'TCP')
            ).first()
            
            if open_port:
                open_port.last_seen = now
                open_port.state = port_data.get('state', 'Open')
                open_port.response_time = str(port_data.get('response_time', '0'))
                updated_count += 1
            else:
                new_port = OpenPort(
                    device_id=device.id,
                    ip_address=ip,
                    port=port_num,
                    protocol=port_data.get('protocol', 'TCP'),
                    service_guess=port_data.get('service', '—'),
                    state=port_data.get('state', 'Open'),
                    response_time=str(port_data.get('response_time', '0')),
                    first_seen=now,
                    last_seen=now,
                    source_module="PortScope"
                )
                db.add(new_port)
                saved_count += 1
                
        try:
            db.commit()
            if saved_count > 0 or updated_count > 0:
                logger.info(f"PortScope sync: {saved_count} new ports, {updated_count} updated.")
            return True, saved_count, updated_count
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving PortScope results: {e}")
            return False, 0, 0

    @staticmethod
    def get_device_web_services(db: Session, device_id: int):
        return db.query(WebService).filter(WebService.device_id == device_id).all()

    @staticmethod
    def save_webpulse_results(db: Session, results: list):
        """
        results: List of dictionaries matching the WebPulse result format.
        """
        saved_count = 0
        updated_count = 0
        
        for res in results:
            url = res.get("url")
            host = res.get("host")
            if not url or not host:
                continue

            # Try to match device by IP or hostname
            device = db.query(Device).filter(Device.ip_address == host).first()
            if not device:
                device = db.query(Device).filter(Device.detected_hostname == host).first()
                
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create stub device if it doesn't exist
            if not device:
                # Is it an IP address? We'll assume yes if it looks like one, else it's a hostname
                is_ip = host.replace(".", "").isdigit()
                ip_addr = host if is_ip else "—"
                hostname = host if not is_ip else "—"
                
                device = Device(
                    ip_address=ip_addr,
                    name="—",
                    detected_hostname=hostname,
                    mac_address="—",
                    vendor="—",
                    device_type="Unclassified",
                    status="Online",
                    tags="",
                    notes="",
                    discovery_source="—",
                    confidence="—",
                    first_seen=now,
                    last_seen=now,
                    response_time="0",
                    source_module="WebPulse"
                )
                db.add(device)
                db.flush()

            # Attempt to find the matching service_id
            port_num = int(res.get("port", 80))
            open_port = db.query(OpenPort).filter(
                OpenPort.device_id == device.id,
                OpenPort.port == port_num
            ).first()
            
            service_id = open_port.id if open_port else None
            
            # Check if web service already exists
            web_service = db.query(WebService).filter(
                WebService.device_id == device.id,
                WebService.url == url
            ).first()

            if web_service:
                web_service.status = res.get("status", "Offline")
                web_service.http_code = res.get("http_code", "—")
                web_service.reason = res.get("reason", "—")
                web_service.final_url = res.get("final_url", "—")
                web_service.redirect_count = res.get("redirect_count", "0")
                web_service.page_title = res.get("title", "—")
                web_service.server_header = res.get("server", "—")
                web_service.content_type = res.get("content_type", "—")
                web_service.ssl_enabled = res.get("ssl_enabled", "—")
                web_service.ssl_expiry = res.get("ssl_expiry", "—")
                web_service.ssl_issuer = res.get("ssl_issuer", "—")
                web_service.error_message = res.get("error", "—")
                web_service.response_time = res.get("response_time", "timeout")
                web_service.last_checked = now
                if service_id:
                    web_service.service_id = service_id
                updated_count += 1
            else:
                new_ws = WebService(
                    device_id=device.id,
                    service_id=service_id,
                    ip_address=device.ip_address,
                    url=url,
                    scheme=res.get("scheme", "—"),
                    host=host,
                    port=port_num,
                    status=res.get("status", "Offline"),
                    http_code=res.get("http_code", "—"),
                    reason=res.get("reason", "—"),
                    final_url=res.get("final_url", "—"),
                    redirect_count=res.get("redirect_count", "0"),
                    page_title=res.get("title", "—"),
                    server_header=res.get("server", "—"),
                    content_type=res.get("content_type", "—"),
                    ssl_enabled=res.get("ssl_enabled", "—"),
                    ssl_expiry=res.get("ssl_expiry", "—"),
                    ssl_issuer=res.get("ssl_issuer", "—"),
                    error_message=res.get("error", "—"),
                    response_time=res.get("response_time", "timeout"),
                    first_seen=now,
                    last_checked=now,
                    source_module="WebPulse"
                )
                db.add(new_ws)
                saved_count += 1

        try:
            db.commit()
            if saved_count > 0 or updated_count > 0:
                logger.info(f"WebPulse sync: {saved_count} new web services, {updated_count} updated.")
            return True, saved_count, updated_count
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving WebPulse results: {e}")
            return False, 0, 0
