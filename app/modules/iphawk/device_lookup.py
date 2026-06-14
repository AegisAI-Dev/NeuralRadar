import os
import csv
from app.core.logger import logger

class DeviceLookup:
    def __init__(self):
        self.devices_db = {}
        self.csv_path = os.path.join("data", "devices.local.csv")
        self.load_csv()

    def load_csv(self):
        if not os.path.exists(self.csv_path):
            return
            
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    ip = row.get("IP", "").strip()
                    if ip:
                        self.devices_db[ip] = {
                            "DisplayName": row.get("DisplayName", "").strip(),
                            "DeviceType": row.get("DeviceType", "").strip(),
                            "VendorOverride": row.get("VendorOverride", "").strip(),
                            "Notes": row.get("Notes", "").strip()
                        }
                        count += 1
                if count > 0:
                    logger.info(f"Loaded {count} custom device overrides from {self.csv_path}")
        except Exception as e:
            logger.error(f"Error loading {self.csv_path}: {e}")

    def get_override(self, ip: str):
        return self.devices_db.get(ip)

device_db = DeviceLookup()
