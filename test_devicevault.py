import sys
import os

# Add the parent directory to sys.path so 'app' is recognized as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.modules.devicevault.service import DeviceVaultService
from app.modules.devicevault.models import Device

def run_tests():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    print("In-memory test DB initialized.")

    # 1. Test Sync: New Device
    host1 = {
        'ip': '192.168.1.100',
        'mac': 'AA:BB:CC:DD:EE:11',
        'display_name': 'TestPC',
        'hostname': 'test-pc.home',
        'vendor': 'Apple',
        'device_type': 'Unclassified',
        'source': 'ARP',
        'confidence': 'High',
        'response_time': 5
    }

    success, saved, updated = DeviceVaultService.save_scan_results(db, [host1])
    print(f"Test 1 - Saved: {saved}, Updated: {updated}")
    assert saved == 1
    assert updated == 0

    # 2. Test Sync: Existing Device Update
    host1_updated = {
        'ip': '192.168.1.100',
        'mac': 'AA:BB:CC:DD:EE:11',
        'display_name': 'TestPC',
        'hostname': 'test-pc-new.home',
        'vendor': 'Apple',
        'device_type': 'Unclassified',
        'source': 'ARP',
        'confidence': 'High',
        'response_time': 2
    }

    success, saved, updated = DeviceVaultService.save_scan_results(db, [host1_updated])
    print(f"Test 2 - Saved: {saved}, Updated: {updated}")
    assert saved == 0
    assert updated == 1

    device = db.query(Device).filter_by(ip_address='192.168.1.100').first()
    assert device.detected_hostname == 'test-pc-new.home'
    assert device.response_time == '2'

    # 3. Test Manual Edit Preservation
    DeviceVaultService.update_manual_fields(db, device.id, "My Awesome PC", "Laptop", "test-tag", "User notes")
    
    host1_again = {
        'ip': '192.168.1.100',
        'mac': 'AA:BB:CC:DD:EE:11',
        'display_name': 'BadNameFromScanner',
        'hostname': 'test-pc-new.home',
        'vendor': 'Apple',
        'device_type': 'Unclassified',
        'source': 'ARP',
        'confidence': 'High',
        'response_time': 1
    }

    DeviceVaultService.save_scan_results(db, [host1_again])
    db.expire_all()
    device = db.query(Device).filter_by(ip_address='192.168.1.100').first()
    
    print(f"Test 3 - Name: {device.name}, Type: {device.device_type}, Tags: {device.tags}")
    assert device.name == "My Awesome PC"
    assert device.device_type == "Laptop"
    assert device.tags == "test-tag"
    assert device.notes == "User notes"

    print("All backend tests passed perfectly!")

if __name__ == "__main__":
    run_tests()
