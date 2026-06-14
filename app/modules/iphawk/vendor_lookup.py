import os
import csv
import re
from app.core.logger import logger

# Large built-in dictionary of common OUIs
BUILTIN_OUI = {
    # ASUSTek
    "60:CF:84": "ASUSTek",
    "04:D4:C4": "ASUSTek",
    "F4:B3:01": "ASUSTek",
    "E0:D5:5E": "ASUSTek",
    
    # Raspberry Pi
    "B8:27:EB": "Raspberry Pi Foundation",
    "DC:A6:32": "Raspberry Pi Trading",
    "E4:5F:01": "Raspberry Pi Trading",
    
    # Synology
    "00:11:32": "Synology",
    
    # Intel
    "00:1B:21": "Intel",
    "00:15:17": "Intel",
    "C8:D9:D2": "Intel",
    "CC:15:31": "Intel",
    
    # Realtek
    "00:E0:4C": "Realtek",
    "52:54:00": "Realtek/QEMU",
    
    # Apple
    "00:16:CB": "Apple",
    "00:1C:B3": "Apple",
    "00:26:BB": "Apple",
    "D8:3A:DD": "Apple",
    "AC:87:A3": "Apple",
    
    # Samsung
    "00:12:47": "Samsung",
    "00:15:99": "Samsung",
    
    # Dell
    "00:14:22": "Dell",
    "00:24:E8": "Dell",
    "F8:DB:88": "Dell",
    
    # HP
    "00:0E:7F": "HP",
    "00:11:0A": "HP",
    "D8:D3:85": "HP",
    
    # Lenovo
    "00:50:8D": "Lenovo",
    "60:6C:66": "Lenovo",
    
    # Microsoft
    "00:15:5D": "Microsoft (Hyper-V)",
    "00:50:F2": "Microsoft",
    "C8:3A:35": "Microsoft",
    
    # TP-Link
    "00:0A:EB": "TP-Link",
    "00:1D:0F": "TP-Link",
    "F4:F2:6D": "TP-Link",
    "C0:25:E9": "TP-Link",
    
    # Ubiquiti
    "00:27:22": "Ubiquiti",
    "04:18:D6": "Ubiquiti",
    "24:A4:3C": "Ubiquiti",
    "F0:9F:C2": "Ubiquiti",
    "E0:63:DA": "Ubiquiti",
    "80:2A:A8": "Ubiquiti",
    
    # MikroTik
    "00:0C:42": "MikroTik",
    "D4:CA:6D": "MikroTik",
    "4C:5E:0C": "MikroTik",
    "E4:8D:8C": "MikroTik",
    
    # Netgear
    "00:09:5B": "Netgear",
    "00:14:6C": "Netgear",
    "A0:04:60": "Netgear",
    
    # Cisco
    "00:00:0C": "Cisco",
    "00:01:42": "Cisco",
    "00:01:43": "Cisco",
    "00:01:63": "Cisco",
    "00:01:64": "Cisco",
    
    # MSI
    "00:16:17": "MSI",
    "00:1F:D0": "MSI",
    "4C:CC:6A": "MSI",
    
    # Gigabyte
    "00:1A:4D": "Gigabyte",
    "00:24:1D": "Gigabyte",
    "1C:1B:0D": "Gigabyte",
    "E0:D5:5E": "Gigabyte",
    
    # VMware
    "00:05:69": "VMware",
    "00:0C:29": "VMware",
    "00:1C:14": "VMware",
    "00:50:56": "VMware",
    
    # VirtualBox
    "08:00:27": "VirtualBox",
    
    # QEMU/Proxmox
    "52:54:00": "QEMU/KVM",
    "BC:24:11": "QEMU/Proxmox",
    "FE:FF:FF": "Proxmox (Virtual)",
    
    # Docker / Virtual
    "02:42:AC": "Docker",
    
    # Lite-On
    "00:A0:D1": "Lite-On",
    
    # AzureWave
    "00:1A:3B": "AzureWave",
    "E0:B9:A5": "AzureWave",
    "DC:85:DE": "AzureWave",
    
    # Hon Hai / Foxconn
    "00:16:CE": "Hon Hai (Foxconn)",
    "00:1E:4C": "Hon Hai (Foxconn)"
}

class VendorLookup:
    def __init__(self):
        self.oui_db = BUILTIN_OUI.copy()
        self.csv_path = os.path.join("data", "oui.csv")
        self.load_csv()

    def normalize_mac(self, mac: str) -> str:
        """Normalizes various MAC formats into AA:BB:CC:DD:EE:FF."""
        clean_mac = mac.replace("-", ":").strip().upper()
        
        # Check if it's already properly formatted
        if re.match(r'^([0-9A-F]{2}:){5}[0-9A-F]{2}$', clean_mac):
            return clean_mac
            
        # In case there are no separators (AABBCCDDEEFF)
        clean_mac = re.sub(r'[^0-9A-F]', '', clean_mac)
        if len(clean_mac) == 12:
            return ":".join(clean_mac[i:i+2] for i in range(0, 12, 2))
            
        return mac.upper()

    def load_csv(self):
        """Loads optional data/oui.csv into the internal DB."""
        if not os.path.exists(self.csv_path):
            return
            
        try:
            with open(self.csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    oui = row.get("OUI", "").strip().upper()
                    vendor = row.get("Vendor", "").strip()
                    if oui and vendor:
                        # Normalize OUI to standard AA:BB:CC just in case
                        oui = oui.replace("-", ":")
                        if len(oui) > 8: # If full MAC is provided, extract OUI
                            oui = oui[:8]
                        if len(oui) == 8:
                            self.oui_db[oui] = vendor
                            count += 1
                if count > 0:
                    logger.info(f"Loaded {count} custom OUI entries from {self.csv_path}")
        except Exception as e:
            logger.error(f"Error loading {self.csv_path}: {e}")

    def get_vendor(self, mac: str) -> str:
        """Looks up the vendor for a given MAC address."""
        if not mac or mac == "Pending...":
            return "Unknown"
            
        normalized = self.normalize_mac(mac)
        
        if len(normalized) >= 8:
            oui = normalized[:8]
            vendor = self.oui_db.get(oui, "Unknown")
            logger.debug(f"Vendor Lookup: Original='{mac}' | Normalized='{normalized}' | OUI='{oui}' | Vendor='{vendor}'")
            return vendor
            
        logger.debug(f"Vendor Lookup failed: invalid length for normalized MAC '{normalized}'")
        return "Unknown"

# Singleton instance
vendor_db = VendorLookup()
