import asyncio
import time
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from app.core.logger import logger
from app.modules.portscope.service_map import get_service_name

class PortScannerThread(QThread):
    port_found = Signal(dict)
    scan_finished = Signal()
    progress_update = Signal(str)

    def __init__(self, ip: str, ports: list):
        super().__init__()
        self.ip = ip
        self.ports = ports
        self._is_running = True
        self.tasks = []

    def stop(self):
        self._is_running = False
        logger.info("Cancellation requested in PortScannerThread.")

    def run(self):
        try:
            total_ports = len(self.ports)
            self.progress_update.emit(f"Scanning {total_ports} ports on {self.ip}...")
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.scan_ports())
            loop.close()
            
        except Exception as e:
            logger.error(f"Error during port scan: {e}")
        finally:
            if not self._is_running:
                logger.info("PortScannerThread exited cleanly after cancellation.")
            else:
                logger.info("PortScannerThread exited cleanly.")
            self.scan_finished.emit()

    async def scan_ports(self):
        sem = asyncio.Semaphore(50)  # Safe concurrency limit for TCP connects
        
        async def bounded_scan(port):
            async with sem:
                if not self._is_running:
                    return None
                return await self.check_port(port)

        self.tasks = [asyncio.create_task(bounded_scan(p)) for p in self.ports]
        monitor_task = asyncio.create_task(self.monitor_cancellation())
        
        results = await asyncio.gather(*self.tasks, return_exceptions=True)
        
        if not monitor_task.done():
            monitor_task.cancel()

        for result in results:
            if isinstance(result, Exception):
                if not isinstance(result, asyncio.CancelledError):
                    logger.debug(f"Port scan task exception: {result}")
                continue
            
            # If we get a valid result back and we aren't cancelling
            if result and self._is_running:
                self.port_found.emit(result)

    async def monitor_cancellation(self):
        while True:
            if not self._is_running:
                cancelled_count = 0
                for task in self.tasks:
                    if not task.done():
                        task.cancel()
                        cancelled_count += 1
                logger.info(f"Cancelled {cancelled_count} pending port checks.")
                break
            await asyncio.sleep(0.1)

    async def check_port(self, port: int):
        start_time = time.time()
        try:
            # Safe basic TCP connect. 1.0s timeout is usually sufficient for LAN.
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.ip, port),
                timeout=1.0
            )
            
            end_time = time.time()
            response_time = round((end_time - start_time) * 1000, 2)
            
            # Immediately close the connection - no banner grabbing yet
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass
                
            return {
                "ip": self.ip,
                "port": port,
                "protocol": "TCP",
                "service": get_service_name(port),
                "state": "Open",
                "response_time": response_time,
                "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        except asyncio.TimeoutError:
            return None
        except ConnectionRefusedError:
            return None
        except asyncio.CancelledError:
            raise
        except Exception as e:
            return None
