import asyncio
import platform
import subprocess
import ipaddress
import time
import socket
import re
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from app.core.logger import logger

class ScannerThread(QThread):
    host_found = Signal(dict)
    mac_resolved = Signal(str, str, str)
    scan_finished = Signal()
    progress_update = Signal(str)

    def __init__(self, subnet):
        super().__init__()
        self.subnet = subnet
        self._is_running = True
        self.os_type = platform.system().lower()
        self.tasks = []

    def stop(self):
        self._is_running = False
        logger.info("Cancellation requested in ScannerThread.")

    def run(self):
        try:
            network = ipaddress.ip_network(self.subnet, strict=False)
            hosts = list(network.hosts())
            total_hosts = len(hosts)
            
            self.progress_update.emit(f"Scanning {total_hosts} hosts...")
            
            # Ensure an event loop is set for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.scan_hosts(hosts))
            loop.close()
            
            if self._is_running:
                # Read ARP table as a fallback to get MAC addresses
                self.read_arp_table()

        except Exception as e:
            logger.error(f"Error during scan: {e}")
        finally:
            if not self._is_running:
                logger.info("ScannerThread exited cleanly after cancellation.")
            else:
                logger.info("ScannerThread exited cleanly.")
            self.scan_finished.emit()

    async def scan_hosts(self, hosts):
        sem = asyncio.Semaphore(64)
        
        async def bounded_ping(host):
            async with sem:
                if not self._is_running:
                    return None
                return await self.ping_host(str(host))

        self.tasks = [asyncio.create_task(bounded_ping(host)) for host in hosts]
        
        # Monitor cancellation
        monitor_task = asyncio.create_task(self.monitor_cancellation())
        
        results = await asyncio.gather(*self.tasks, return_exceptions=True)
        
        if not monitor_task.done():
            monitor_task.cancel()

        for result in results:
            if isinstance(result, Exception):
                if not isinstance(result, asyncio.CancelledError):
                    logger.debug(f"Task exception: {result}")
                continue
                
            if result and result.get('is_up'):
                if not self._is_running:
                    logger.info(f"Ignored late result for {result['ip']} due to cancellation.")
                    continue
                    
                from app.modules.iphawk.device_lookup import device_db
                
                hostname, source = self.get_hostname(result['ip'])
                
                confidence = "Medium"
                is_suspicious = False
                if source == "Unknown":
                    confidence = "Low"
                    is_suspicious = True
                else:
                    low_indicators = ["host.docker.internal", "gateway.docker.internal", "docker", "localhost", "unknown"]
                    hn_lower = hostname.lower()
                    for ind in low_indicators:
                        if ind in hn_lower:
                            confidence = "Low"
                            is_suspicious = True
                            break

                device_type = "Unclassified"
                vendor_override = ""
                manual_override = "No"
                vendor_over_applied = "No"
                notes = ""
                display_name = ""
                
                # Check for manual overrides first
                override = device_db.get_override(result['ip'])
                display_name = ""
                if override:
                    confidence = "High"
                    source = "Manual Override"
                    manual_override = "Yes"
                    notes = override.get("Notes", "")
                    if override["DisplayName"]:
                        display_name = override["DisplayName"]
                    if override["DeviceType"]:
                        device_type = override["DeviceType"]
                    if override["VendorOverride"]:
                        vendor_override = override["VendorOverride"]
                        vendor_over_applied = "Yes"
                
                # If no manual display_name, evaluate detected hostname
                if not display_name:
                    if hostname and hostname.lower() not in ["", "unknown", "none", "null", "host.docker.internal", "gateway.docker.internal", "localhost"] and "docker" not in hostname.lower() and hostname != result['ip']:
                        display_name = hostname
                    else:
                        display_name = "—"

                result['hostname'] = hostname
                result['display_name'] = display_name
                result['device_type'] = device_type
                result['vendor_override'] = vendor_override
                result['source'] = source
                result['confidence'] = confidence
                result['manual_override'] = manual_override
                result['vendor_over_applied'] = vendor_over_applied
                result['notes'] = notes
                result['mac'] = "—"
                result['vendor'] = "—"
                result['last_seen'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                self.host_found.emit(result)

    async def monitor_cancellation(self):
        while True:
            if not self._is_running:
                cancelled_count = 0
                for task in self.tasks:
                    if not task.done():
                        task.cancel()
                        cancelled_count += 1
                logger.info(f"Cancelled {cancelled_count} pending tasks.")
                break
            await asyncio.sleep(0.1)

    async def ping_host(self, ip):
        if self.os_type == "windows":
            cmd = f"ping -n 1 -w 1000 {ip}"
        else:
            cmd = f"ping -c 1 -W 1 {ip}"

        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
        except Exception as e:
            logger.debug(f"Failed to create subprocess for {ip}: {e}")
            return None

        start_time = time.time()
        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=1.5)
            end_time = time.time()
            
            response_time = round((end_time - start_time) * 1000, 2)
            output = stdout.decode('utf-8', errors='ignore').lower()
            
            is_up = False
            if process.returncode == 0:
                if "unreachable" not in output and "ttl=" in output:
                    is_up = True
                    
            if is_up:
                return {"ip": ip, "is_up": True, "response_time": response_time}
            return None
            
        except asyncio.TimeoutError:
            if process.returncode is None:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            logger.debug(f"Ping subprocess timed out for {ip}")
            return None
        except asyncio.CancelledError:
            if process.returncode is None:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            raise
        except Exception as e:
            logger.debug(f"Ping failed for {ip}: {e}")
            return None

    def get_hostname(self, ip):
        try:
            name = socket.gethostbyaddr(ip)[0]
            return name, "socket.gethostbyaddr"
        except socket.herror:
            return "Unknown", "Unknown"
        except Exception:
            return "Unknown", "Unknown"

    def read_arp_table(self):
        if not self._is_running:
            return
            
        self.progress_update.emit("Resolving MAC addresses...")
        try:
            from app.modules.iphawk.vendor_lookup import vendor_db
            
            cmd = "arp -a" if self.os_type == "windows" else "arp -an"
            output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore')
            
            pattern = re.compile(r'(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?(?P<mac>[0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2}[:-][0-9A-Fa-f]{2})')
            
            for match in pattern.finditer(output):
                ip = match.group('ip')
                raw_mac = match.group('mac')
                mac = vendor_db.normalize_mac(raw_mac)
                vendor = vendor_db.get_vendor(mac)
                
                self.mac_resolved.emit(ip, mac, vendor)
                
        except Exception as e:
            logger.error(f"ARP table read error: {e}")
