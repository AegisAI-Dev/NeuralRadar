import re
import time
import socket
import ssl
import requests
import urllib3
from urllib.parse import urlparse
from datetime import datetime
from PySide6.QtCore import QThread, Signal
from app.core.logger import logger

# Disable warnings for unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebPulseCheckerThread(QThread):
    check_finished = Signal(dict)
    progress_update = Signal(str)

    worker_finished = Signal()

    def __init__(self, url: str, allow_insecure: bool = False):
        super().__init__()
        self.url = url
        self.allow_insecure = allow_insecure
        self._is_running = True
        self.session = None

    def stop(self):
        self._is_running = False
        logger.info(f"Cancellation requested for WebPulse check on {self.url}")
        if self.session:
            try:
                self.session.close()
            except Exception as e:
                logger.debug(f"Error closing session during cancellation: {e}")

    def run(self):
        try:
            if not self._is_running:
                return
                
            self.progress_update.emit(f"Checking {self.url}...")
            result = self.check_url(self.url)
            
            if self._is_running:
                self.check_finished.emit(result)
            else:
                logger.info(f"Worker for {self.url} cancelled, discarding result.")
                
        except Exception as e:
            logger.error(f"WebPulse error on {self.url}: {e}")
            if self._is_running:
                self.check_finished.emit({
                    "url": self.url,
                    "status": "Error",
                    "http_code": "—",
                    "title": "—",
                    "server": "—",
                    "ssl_expiry": "—",
                    "response_time": "—",
                    "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": str(e),
                    "scheme": "—",
                    "host": "—",
                    "port": "—",
                    "reason": "—",
                    "final_url": "—",
                    "redirect_count": "—",
                    "content_type": "—",
                    "ssl_enabled": "—",
                    "ssl_issuer": "—"
                })
        finally:
            logger.info(f"Worker for {self.url} finished.")
            self.worker_finished.emit()

    def perform_http_request(self, url, verify, timeout=(1.5, 2.0)):
        if self.session:
            try: self.session.close()
            except: pass
            
        self.session = requests.Session()
        self.session.verify = verify
        
        response = self.session.head(url, timeout=timeout, allow_redirects=True)
        if not self._is_running:
            return None
            
        if response.status_code == 405: # Method Not Allowed
            response = self.session.get(url, timeout=timeout, allow_redirects=True, stream=True)
        elif response.status_code < 400:
            # We limit downloading huge files using stream=True
            response = self.session.get(url, timeout=timeout, allow_redirects=True, stream=True)
            
        return response

    def parse_http_response(self, response, res, start_time):
        end_time = time.time()
        res["response_time"] = str(int((end_time - start_time) * 1000))
        
        res["http_code"] = str(response.status_code)
        res["reason"] = response.reason
        res["final_url"] = response.url
        res["redirect_count"] = str(len(response.history))
        res["server"] = response.headers.get("Server", "—")
        res["content_type"] = response.headers.get("Content-Type", "—")
        
        if response.status_code < 300:
            res["status"] = "Online"
        elif response.status_code < 400:
            res["status"] = "Redirect Warning"
        else:
            res["status"] = f"Error {response.status_code}"

        if "text/html" in res["content_type"].lower():
            # Read at most 10KB to avoid large payloads
            content = response.raw.read(10240, decode_content=True)
            if content:
                text_content = content.decode('utf-8', errors='ignore')
                match = re.search(r'<title[^>]*>(.*?)</title>', text_content, re.IGNORECASE | re.DOTALL)
                if match:
                    title = match.group(1).strip()
                    title = re.sub(r'\s+', ' ', title)
                    res["title"] = title[:100]
                    if not res["title"]:
                        res["title"] = "—"

    def check_url(self, url: str) -> dict:
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        host = parsed.hostname
        port = parsed.port or (443 if scheme == 'https' else 80)
        
        start_time = time.time()
        
        res = {
            "url": url,
            "status": "Offline",
            "http_code": "—",
            "title": "—",
            "server": "—",
            "ssl_expiry": "—",
            "response_time": "timeout",
            "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error": "—",
            "scheme": scheme,
            "host": host,
            "port": str(port),
            "reason": "—",
            "final_url": "—",
            "redirect_count": "0",
            "content_type": "—",
            "ssl_enabled": "True" if scheme == 'https' else "False",
            "ssl_issuer": "—"
        }

        # Try SSL check if https
        if scheme == 'https':
            ssl_info = self.get_ssl_info(host, port)
            res["ssl_expiry"] = ssl_info.get("expiry", "—")
            res["ssl_issuer"] = ssl_info.get("issuer", "—")
            if ssl_info.get("error"):
                res["error"] = ssl_info["error"]
                if ssl_info.get("protocol_mismatch"):
                    res["status"] = "Protocol Mismatch"
                    res["ssl_enabled"] = "False"
                elif ssl_info.get("sni_error"):
                    res["status"] = "TLS/SNI Error"
                    res["ssl_enabled"] = "Unknown"

        if not self._is_running:
            return res

        # Check HTTP
        response = None
        try:
            response = self.perform_http_request(url, verify=True)
            if not self._is_running or not response:
                return res
            
            self.parse_http_response(response, res, start_time)
            
            # If verify=True succeeds but we still had an SSL warning from our custom checker
            if res["status"] in ["Online", "Redirect Warning"] and res["error"] != "—":
                if res.get("status") != "Protocol Mismatch":
                    res["status"] = "TLS Warning"

        except requests.exceptions.Timeout:
            logger.debug(f"HTTP request timed out for {url}")
            res["status"] = "Offline"
            res["error"] = "Connection timed out"
        except requests.exceptions.SSLError as e:
            err_str = str(e).lower()
            logger.debug(f"SSL verification failed for {url}: {err_str}")
            
            if "wrong_version_number" in err_str or res.get("status") == "Protocol Mismatch":
                res["status"] = "Protocol Mismatch"
                res["ssl_enabled"] = "False"
                res["response_time"] = "SSL Handshake Failed"
                if res["error"] == "—" or "SSL Verification Failed" in res["error"]:
                    res["error"] = f"HTTPS was requested, but this port appears to speak plain HTTP or another non-TLS protocol. Suggest retry URL: http://{host}:{port}"
                    
            elif any(x in err_str for x in ["tlsv1_unrecognized_name", "unrecognized name", "handshake failure", "server name indication", "sni"]) or res.get("status") == "TLS/SNI Error":
                res["status"] = "TLS/SNI Error"
                res["ssl_enabled"] = "Unknown"
                res["response_time"] = "SSL Handshake Failed"
                if res["error"] == "—" or "SSL Verification Failed" in res["error"]:
                    res["error"] = "Server rejected the requested hostname/SNI. Try using the correct domain name instead of the IP address.\n\nHint: HTTPS virtual hosts often require a domain name. Try the service using its configured hostname instead of the IP address."
            else:
                res["status"] = "TLS Warning"
                if res["error"] == "—":
                    res["error"] = "SSL Verification Failed"
                    
                if self.allow_insecure:
                    logger.info(f"Retrying {url} with verify=False")
                    if response:
                        try: response.close()
                        except: pass
                    
                    try:
                        response = self.perform_http_request(url, verify=False)
                        if not self._is_running or not response:
                            return res
                            
                        self.parse_http_response(response, res, start_time)
                        # Override status to keep the warning visible despite HTTP success
                        res["status"] = "TLS Warning"
                    except Exception as insecure_e:
                        logger.debug(f"Insecure retry failed for {url}: {insecure_e}")
        except requests.exceptions.ConnectionError:
            logger.debug(f"Connection refused for {url}")
            res["status"] = "Offline"
            res["error"] = "Connection refused or host unreachable"
        except Exception as e:
            logger.debug(f"Unexpected error for {url}: {e}")
            res["status"] = "Error"
            res["error"] = str(e)
        finally:
            if response:
                try:
                    response.close()
                except Exception:
                    pass
            if self.session:
                try:
                    self.session.close()
                except Exception:
                    pass
                self.session = None

        return res

    def get_ssl_info(self, host, port):
        info = {"expiry": "—", "issuer": "—", "error": None}
        context = ssl.create_default_context()
        context.check_hostname = False
        
        try:
            with socket.create_connection((host, port), timeout=2.0) as sock:
                if not self._is_running:
                    return info
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    if not self._is_running:
                        return info
                    cert = ssock.getpeercert()
                    if cert:
                        info["expiry"] = cert.get("notAfter", "—")
                        # Format issuer safely
                        issuer_parts = []
                        for entry in cert.get("issuer", []):
                            for sub_entry in entry:
                                issuer_parts.append(f"{sub_entry[0]}={sub_entry[1]}")
                        if issuer_parts:
                            # Try to extract Organization or Common Name
                            for part in issuer_parts:
                                if part.startswith("organizationName="):
                                    info["issuer"] = part.split("=", 1)[1]
                                    break
                            else:
                                for part in issuer_parts:
                                    if part.startswith("commonName="):
                                        info["issuer"] = part.split("=", 1)[1]
                                        break
                                else:
                                    info["issuer"] = issuer_parts[0].split("=", 1)[1]
                        else:
                            info["issuer"] = "—"
        except socket.timeout:
            logger.debug(f"SSL socket timeout for {host}:{port}")
            info["error"] = "SSL connection timed out"
        except ssl.SSLCertVerificationError as e:
            logger.debug(f"SSL Verification Error for {host}:{port}")
            info["error"] = "Untrusted or Self-Signed Certificate"
        except ssl.SSLError as e:
            err_str = str(e).lower()
            logger.debug(f"SSL Error for {host}:{port}: {err_str}")
            if "wrong_version_number" in err_str:
                info["error"] = f"HTTPS was requested, but this port appears to speak plain HTTP or another non-TLS protocol. Suggest retry URL: http://{host}:{port}"
                info["protocol_mismatch"] = True
            elif any(x in err_str for x in ["tlsv1_unrecognized_name", "unrecognized name", "handshake failure", "server name indication", "sni"]):
                info["error"] = "Server rejected the requested hostname/SNI. Try using the correct domain name instead of the IP address.\n\nHint: HTTPS virtual hosts often require a domain name. Try the service using its configured hostname instead of the IP address."
                info["sni_error"] = True
            else:
                info["error"] = f"SSL Error: {str(e)}"
        except Exception as e:
            logger.debug(f"SSL error for {host}:{port}: {e}")
            info["error"] = f"SSL Error: {e}"
            
        return info
