PORT_SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    587: "SMTP Submission",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL/MariaDB",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8006: "Proxmox",
    8080: "HTTP Alternate",
    8443: "HTTPS Alternate",
    9090: "Web/Admin",
    9443: "HTTPS Admin"
}

def get_service_name(port: int) -> str:
    return PORT_SERVICES.get(port, "—")
