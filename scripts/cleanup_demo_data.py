import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import SessionLocal
from app.modules.devicevault.models import Device, OpenPort

def cleanup():
    db = SessionLocal()
    demo_names = [
        "My Awesome PC",
        "My Awsome PC",
        "Test Router",
        "Laptop",
        "Demo Device",
        "Example Device",
        "BadNameFromScanner"
    ]
    
    deleted_count = 0
    try:
        devices = db.query(Device).filter(Device.name.in_(demo_names)).all()
        for device in devices:
            db.delete(device)
            deleted_count += 1
            
        db.commit()
        print(f"Cleanup successful. Removed {deleted_count} demo devices.")
    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup()
