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

    @staticmethod
    def get_inventory_stats(db: Session):
        """Lightweight stats for dashboard. Uses existing models only."""
        stats = {
            'total_devices': 0,
            'online_devices': 0,
            'open_services': 0,
            'web_endpoints': 0,
            'tls_warnings': 0,
            'last_updated': '—'
        }
        
        try:
            # Total and Online Devices
            stats['total_devices'] = db.query(Device).count()
            stats['online_devices'] = db.query(Device).filter(Device.status == "Online").count()
            
            # Open Services
            stats['open_services'] = db.query(OpenPort).count()
            
            # Web Endpoints
            stats['web_endpoints'] = db.query(WebService).count()
            
            # TLS Warnings (matches existing status values)
            tls_statuses = ["TLS Warning", "TLS/SNI Error", "Protocol Mismatch"]
            stats['tls_warnings'] = db.query(WebService).filter(
                WebService.status.in_(tls_statuses)
            ).count()
            
            # Last Updated - simple max from devices (lightweight)
            latest_device = db.query(Device).order_by(Device.last_seen.desc()).first()
            if latest_device and latest_device.last_seen:
                stats['last_updated'] = latest_device.last_seen
            
        except Exception as e:
            logger.error(f"Stats calculation error: {e}")
            
        return stats

    @staticmethod
    def get_filtered_devices(db: Session, query: str = "", status_filter: str = "All", device_type_filter: str = "All", vendor_filter: str = "All", hygiene_filter: str = None):
        """Advanced filtered query combining search and filters. Uses existing fields only."""
        base_query = db.query(Device)
        
        if query.strip():
            q = f"%{query.strip()}%"
            base_query = base_query.filter(
                (Device.ip_address.ilike(q)) |
                (Device.name.ilike(q)) |
                (Device.detected_hostname.ilike(q)) |
                (Device.mac_address.ilike(q)) |
                (Device.vendor.ilike(q)) |
                (Device.device_type.ilike(q)) |
                (Device.tags.ilike(q)) |
                (Device.notes.ilike(q))
            )
        
        if status_filter != "All":
            base_query = base_query.filter(Device.status == status_filter)
        
        if device_type_filter != "All":
            base_query = base_query.filter(Device.device_type == device_type_filter)
        
        if vendor_filter != "All":
            base_query = base_query.filter(Device.vendor == vendor_filter)
        

        if hygiene_filter == "unclassified":
            base_query = base_query.filter(
                (Device.device_type.is_(None)) |
                (Device.device_type == "") |
                (Device.device_type.ilike("%unclassified%")) |
                (Device.device_type.ilike("%unknown%"))
            )
        elif hygiene_filter == "missing_name":
            base_query = base_query.filter(
                (Device.name.is_(None)) |
                (Device.name == "") |
                (Device.name == "—")
            )
        elif hygiene_filter == "missing_vendor":
            base_query = base_query.filter(
                (Device.vendor.is_(None)) |
                (Device.vendor == "") |
                (Device.vendor.ilike("%unknown%"))
            )
        elif hygiene_filter == "tls_warnings":
            base_query = base_query.join(WebService).filter(
                WebService.status.in_(["TLS Warning", "TLS/SNI Error", "Protocol Mismatch"])
            )
        elif hygiene_filter == "stale":
            from datetime import datetime, timedelta
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            base_query = base_query.filter(Device.last_seen < seven_days_ago)
        elif hygiene_filter == "with_services":
            base_query = base_query.join(OpenPort)
        elif hygiene_filter == "with_web_metadata":
            base_query = base_query.join(WebService)

        return base_query.all()

    @staticmethod
    def bulk_update_device_type(db: Session, device_ids: list[int], device_type: str) -> int:
        """Bulk update device_type for multiple devices. No schema change."""
        if not device_ids:
            return 0
        try:
            updated = db.query(Device).filter(Device.id.in_(device_ids)).update(
                {"device_type": device_type}, synchronize_session=False
            )
            db.commit()
            logger.info(f"Bulk updated device_type to '{device_type}' for {updated} devices")
            return updated
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk device_type update failed: {e}")
            return 0

    @staticmethod
    def bulk_add_tag(db: Session, device_ids: list[int], tag: str) -> int:
        """Bulk add tag to multiple devices without duplicating. No schema change."""
        if not device_ids or not tag or not tag.strip():
            return 0
        tag = tag.strip()
        updated_count = 0
        try:
            for device_id in device_ids:
                device = db.query(Device).filter(Device.id == device_id).first()
                if device:
                    current_tags = device.tags or ""
                    tags_list = [t.strip() for t in current_tags.split(',') if t.strip()]
                    if tag not in tags_list:
                        tags_list.append(tag)
                        device.tags = ','.join(tags_list)
                        updated_count += 1
            db.commit()
            logger.info(f"Bulk added tag '{tag}' to {updated_count} devices")
            return updated_count
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk tag add failed: {e}")
            return 0

    @staticmethod
    def get_inventory_hygiene_summary(db: Session) -> dict:
        """Return inventory hygiene counts using existing models only. No schema changes."""
        summary = {
            'unclassified': 0,
            'missing_name': 0,
            'missing_vendor': 0,
            'has_services': 0,
            'has_web_metadata': 0,
            'tls_warnings': 0,
            'stale': 0
        }
        try:
            # Unclassified
            summary['unclassified'] = db.query(Device).filter(
                (Device.device_type.is_(None)) |
                (Device.device_type == '') |
                (Device.device_type.ilike('%unclassified%')) |
                (Device.device_type.ilike('%unknown%'))
            ).count()
            
            # Missing name
            summary['missing_name'] = db.query(Device).filter(
                (Device.name.is_(None)) |
                (Device.name == '') |
                (Device.name == '—')
            ).count()
            
            # Missing vendor
            summary['missing_vendor'] = db.query(Device).filter(
                (Device.vendor.is_(None)) |
                (Device.vendor == '') |
                (Device.vendor.ilike('%unknown%'))
            ).count()
            
            # Has services (devices with at least 1 open port record)
            summary['has_services'] = db.query(Device).join(OpenPort).distinct().count()
            
            # Has web metadata
            summary['has_web_metadata'] = db.query(Device).join(WebService).distinct().count()
            
            # TLS warnings
            warning_statuses = ["TLS Warning", "TLS/SNI Error", "Protocol Mismatch"]
            summary['tls_warnings'] = db.query(WebService).filter(
                WebService.status.in_(warning_statuses)
            ).count()
            
            # Stale (last_seen > 7 days) - safe parsing
            from datetime import datetime, timedelta
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            summary['stale'] = db.query(Device).filter(
                Device.last_seen < seven_days_ago
            ).count()
            
        except Exception as e:
            logger.error(f"Hygiene summary calculation error: {e}")
        
        return summary

    @staticmethod
    def get_stored_web_endpoints(db: Session):
        """Return unique stored web endpoints from DeviceVault web metadata. No schema change."""
        try:
            from app.modules.devicevault.models import WebService
            results = db.query(WebService.url, Device.ip_address, Device.name.label('device_name'), WebService.status, WebService.last_checked).join(Device, WebService.device_id == Device.id).distinct().all()
            return [{'url': r.url, 'ip_address': r.ip_address, 'device_name': r.device_name, 'status': r.status, 'last_checked': r.last_checked} for r in results]
        except Exception as e:
            logger.error(f"Stored endpoints query error: {e}")
            return []

    @staticmethod
    def get_stored_web_metadata_summary(db: Session):
        """Return summary of stored web metadata for Last Known State table. Uses existing models only."""
        try:
            from app.modules.devicevault.models import WebService, Device
            from datetime import datetime
            results = db.query(
                WebService.url,
                Device.ip_address.label('device_ip'),
                Device.name.label('device_name'),
                WebService.status,
                WebService.http_code,
                WebService.status.label('tls_status'), # Fallback to status since tls_status is not on the model
                WebService.ssl_expiry,
                WebService.server_header,
                WebService.last_checked
            ).join(Device, WebService.device_id == Device.id).all()
            
            summary = []
            today = datetime.now().date()
            for r in results:
                days_until = '—'
                if r.ssl_expiry:
                    try:
                        expiry_date = datetime.strptime(r.ssl_expiry, '%Y-%m-%d').date()
                        days = (expiry_date - today).days
                        days_until = f"{days} days" if days > 0 else "Expired"
                    except:
                        days_until = '—'
                summary.append({
                    'url': r.url or '—',
                    'device': f"{r.device_name or '—'} ({r.device_ip or '—'})",
                    'status': r.status or '—',
                    'http_code': r.http_code or '—',
                    'tls_status': r.tls_status or '—',
                    'ssl_expiry': r.ssl_expiry or '—',
                    'days_until': days_until,
                    'server': r.server_header or '—',
                    'last_checked': r.last_checked or '—'
                })
            return summary
        except Exception as e:
            logger.error(f"Stored web metadata summary error: {e}")
            return []

    @staticmethod
    def get_stored_services_summary(db: Session):
        """Return summary of stored open services for PortScope Stored Services table. Uses existing models only."""
        try:
            from app.modules.devicevault.models import OpenPort, Device
            results = db.query(
                Device.id.label('device_id'),
                Device.name.label('device_name'),
                Device.ip_address,
                OpenPort.port,
                OpenPort.protocol,
                OpenPort.service_guess,
                OpenPort.state,
                OpenPort.response_time,
                OpenPort.last_seen
            ).join(Device, OpenPort.device_id == Device.id).all()
            return [{
                'device_id': r.device_id,
                'device_name': r.device_name or '—',
                'ip_address': r.ip_address or '—',
                'port': r.port,
                'protocol': r.protocol or '—',
                'service': r.service_guess or '—',
                'state': r.state or '—',
                'response_time': r.response_time or '—',
                'last_seen': r.last_seen or '—'
            } for r in results]
        except Exception as e:
            logger.error(f"Stored services summary error: {e}")
            return []

    @staticmethod
    def get_known_devices_summary(db: Session):
        """Return summary of known devices from DeviceVault for IPHawk Known Devices table. Uses existing Device model only."""
        try:
            results = db.query(Device).all()
            summary = []
            for d in results:
                summary.append({
                    'device_id': d.id,
                    'name': d.name or '—',
                    'ip_address': d.ip_address or '—',
                    'mac_address': d.mac_address or '—',
                    'vendor': d.vendor or '—',
                    'device_type': d.device_type or '—',
                    'status': d.status or '—',
                    'last_seen': d.last_seen or '—'
                })
            return summary
        except Exception as e:
            logger.error(f"Known devices summary error: {e}")
            return []

    @staticmethod
    def get_dashboard_intelligence_summary(db: Session) -> dict:
        """Return safe local intelligence summary using existing models only. No network calls."""
        summary = {
            'total_devices': 0,
            'unclassified_devices': 0,
            'missing_names': 0,
            'missing_vendors': 0,
            'stored_open_services': 0,
            'stored_web_endpoints': 0,
            'tls_warnings': 0,
            'expired_tls_count': 0,
            'expiring_tls_count': 0,
            'last_inventory_update': '—'
        }
        try:
            from app.modules.devicevault.models import Device, OpenPort, WebService
            from datetime import datetime, timedelta

            summary['total_devices'] = db.query(Device).count()
            
            summary['unclassified_devices'] = db.query(Device).filter(
                (Device.device_type.is_(None)) |
                (Device.device_type == '') |
                (Device.device_type.ilike('%unclassified%')) |
                (Device.device_type.ilike('%unknown%'))
            ).count()
            
            summary['missing_names'] = db.query(Device).filter(
                (Device.name.is_(None)) |
                (Device.name == '') |
                (Device.name == '—')
            ).count()
            
            summary['missing_vendors'] = db.query(Device).filter(
                (Device.vendor.is_(None)) |
                (Device.vendor == '') |
                (Device.vendor.ilike('%unknown%'))
            ).count()
            
            summary['stored_open_services'] = db.query(OpenPort).count()
            
            summary['stored_web_endpoints'] = db.query(WebService).count()
            
            warning_statuses = ["TLS Warning", "TLS/SNI Error", "Protocol Mismatch"]
            summary['tls_warnings'] = db.query(WebService).filter(
                WebService.status.in_(warning_statuses)
            ).count()
            
            # Expiry calculation (safe parsing)
            today = datetime.now().date()
            for ws in db.query(WebService).filter(WebService.ssl_expiry.isnot(None)).all():
                try:
                    expiry_date = datetime.strptime(ws.ssl_expiry, '%Y-%m-%d').date()
                    days = (expiry_date - today).days
                    if days < 0:
                        summary['expired_tls_count'] += 1
                    elif days <= 30:
                        summary['expiring_tls_count'] += 1
                except:
                    pass
            
            latest = db.query(Device).order_by(Device.last_seen.desc()).first()
            if latest and latest.last_seen:
                summary['last_inventory_update'] = latest.last_seen
            
        except Exception as e:
            logger.error(f"Dashboard intelligence summary error: {e}")
        
        return summary

    @staticmethod
    def get_recent_activity_summary(db: Session, limit: int = 10) -> list:
        """Return recent activity summary from existing stored data only. No writes, no schema change."""
        activities = []
        try:
            from app.modules.devicevault.models import Device, OpenPort, WebService
            from datetime import datetime

            # Recent devices
            recent_devices = db.query(Device).order_by(Device.last_seen.desc()).limit(limit).all()
            for d in recent_devices:
                if d.last_seen:
                    activities.append({
                        'timestamp': d.last_seen,
                        'type': 'device',
                        'title': f"Device seen: {d.name or d.ip_address or 'Unknown'}",
                        'description': f"Status: {d.status or '—'} | Type: {d.device_type or 'Unclassified'}",
                        'source': 'DeviceVault'
                    })
            
            # Recent services
            recent_services = db.query(OpenPort).order_by(OpenPort.last_seen.desc()).limit(limit).all()
            for s in recent_services:
                if s.last_seen:
                    activities.append({
                        'timestamp': s.last_seen,
                        'type': 'service',
                        'title': f"Service observed: {s.ip_address or '—'}:{s.port}",
                        'description': f"Service: {s.service_guess or '—'} | State: {s.state or '—'}",
                        'source': 'DeviceVault'
                    })
            
            # Recent web
            recent_web = db.query(WebService).order_by(WebService.last_checked.desc()).limit(limit).all()
            for w in recent_web:
                if w.last_checked:
                    activities.append({
                        'timestamp': w.last_checked,
                        'type': 'web',
                        'title': f"Web endpoint stored: {w.url or '—'}",
                        'description': f"Status: {w.status or '—'} | TLS: {w.ssl_enabled or '—'}",
                        'source': 'DeviceVault'
                    })
            
            # Sort by timestamp descending and limit
            activities.sort(key=lambda x: x['timestamp'] or '', reverse=True)
            return activities[:limit]
        except Exception as e:
            logger.error(f"Recent activity summary error: {e}")
            return []

    @staticmethod
    def get_device_relationship_summary(db: Session, limit: int = 10) -> list:
        """Return device relationship summary using existing models only. No schema change, no writes."""
        try:
            from app.modules.devicevault.models import Device, OpenPort, WebService
            from sqlalchemy import func

            # Subquery for counts per device
            service_count = db.query(
                OpenPort.device_id,
                func.count(OpenPort.id).label('service_count')
            ).group_by(OpenPort.device_id).subquery()

            web_count = db.query(
                WebService.device_id,
                func.count(WebService.id).label('web_count')
            ).group_by(WebService.device_id).subquery()

            tls_count = db.query(
                WebService.device_id,
                func.count(WebService.id).label('tls_count')
            ).filter(WebService.status.in_(["TLS Warning", "TLS/SNI Error", "Protocol Mismatch"])).group_by(WebService.device_id).subquery()

            results = db.query(
                Device.id,
                Device.name,
                Device.ip_address,
                Device.device_type,
                func.coalesce(service_count.c.service_count, 0).label('service_count'),
                func.coalesce(web_count.c.web_count, 0).label('web_count'),
                func.coalesce(tls_count.c.tls_count, 0).label('tls_attention_count'),
                Device.last_seen
            ).outerjoin(service_count, Device.id == service_count.c.device_id)             .outerjoin(web_count, Device.id == web_count.c.device_id)             .outerjoin(tls_count, Device.id == tls_count.c.device_id)             .order_by(
                (func.coalesce(service_count.c.service_count, 0) + func.coalesce(web_count.c.web_count, 0)).desc(),
                Device.last_seen.desc()
            ).limit(limit).all()

            summary = []
            for r in results:
                summary.append({
                    'device_id': r.id,
                    'name': r.name or r.ip_address or 'Unknown',
                    'ip_address': r.ip_address or '—',
                    'device_type': r.device_type or 'Unclassified',
                    'service_count': r.service_count,
                    'web_endpoint_count': r.web_count,
                    'tls_attention_count': r.tls_attention_count,
                    'last_seen': r.last_seen or '—'
                })
            return summary
        except Exception as e:
            logger.error(f"Device relationship summary error: {e}")
            return []

    @staticmethod
    def get_device_relationship_details(db: Session, device_id: int) -> dict:
        """Return detailed relationship data for a specific device ID. Uses existing models only. No schema change, no writes."""
        try:
            from app.modules.devicevault.models import Device, OpenPort, WebService
            device = db.query(Device).filter(Device.id == device_id).first()
            if not device:
                return None
            services = db.query(OpenPort).filter(OpenPort.device_id == device_id).all()
            web = db.query(WebService).filter(WebService.device_id == device_id).all()
            return {
                'device_id': device.id,
                'name': device.name or device.ip_address or 'Unknown',
                'ip_address': device.ip_address or '—',
                'mac_address': device.mac_address or '—',
                'vendor': device.vendor or '—',
                'device_type': device.device_type or 'Unclassified',
                'status': device.status or '—',
                'last_seen': device.last_seen or '—',
                'services': [{
                    'port': s.port,
                    'protocol': s.protocol or '—',
                    'service': s.service_guess or '—',
                    'state': s.state or '—',
                    'response_time': s.response_time or '—',
                    'last_seen': s.last_seen or '—'
                } for s in services],
                'web_endpoints': [{
                    'url': w.url or '—',
                    'status': w.status or '—',
                    'http_code': w.http_code or '—',
                    'title': w.title or '—',
                    'server': w.server_header or '—',
                    'tls_status': w.tls_status or '—',
                    'ssl_expiry': w.ssl_expiry or '—',
                    'last_checked': w.last_checked or '—'
                } for w in web]
            }
        except Exception as e:
            logger.error(f"Device relationship details error: {e}")
            return None
