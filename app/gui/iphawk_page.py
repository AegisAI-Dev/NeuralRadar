from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QSplitter
)
from PySide6.QtCore import Qt, Slot
from app.modules.iphawk.scanner import ScannerThread
from app.modules.devicevault.service import DeviceVaultService
from app.core.database import SessionLocal
from app.core.logger import logger
from app.gui.theme import Theme
import ipaddress
import socket

class IPHawkPage(QWidget):
    def __init__(self):
        super().__init__()
        self.is_cancelled = False
        self.host_data_map = {}
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("IPHawk")
        title.setStyleSheet(Theme.page_title_style())
        subtitle = QLabel("Local network discovery module")
        subtitle.setStyleSheet(Theme.page_subtitle_style())
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
        # Security Notice
        notice_label = QLabel("⚠️ Only scan networks you own or have permission to test.")
        notice_label.setStyleSheet(Theme.notice_style("warning"))
        main_layout.addWidget(notice_label)
        
        # Controls Area
        controls_frame = QFrame()
        controls_frame.setStyleSheet(Theme.section_frame_style())
        controls_vbox = QVBoxLayout(controls_frame)
        controls_vbox.setSpacing(15)

        # Input and Auto-Detect Row
        input_row = QHBoxLayout()
        self.subnet_input = QLineEdit()
        self.subnet_input.setPlaceholderText("e.g. 192.168.1.0/24")
        self.subnet_input.setStyleSheet(Theme.input_style())
        input_row.addWidget(self.subnet_input)
        
        self.btn_detect = QPushButton("Detect Network")
        self.btn_detect.setStyleSheet(Theme.secondary_btn_style())
        self.btn_detect.clicked.connect(self.detect_network)
        input_row.addWidget(self.btn_detect)
        
        controls_vbox.addLayout(input_row)

        self.detected_label = QLabel("")
        self.detected_label.setStyleSheet(Theme.muted_label_style())
        controls_vbox.addWidget(self.detected_label)

        # Actions Row
        action_row = QHBoxLayout()
        self.btn_start = QPushButton("Start Scan")
        self.btn_start.setStyleSheet(Theme.primary_btn_style())
        self.btn_start.clicked.connect(self.start_scan)
        action_row.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("Stop Scan")
        self.btn_stop.setStyleSheet(Theme.danger_btn_style())
        self.btn_stop.clicked.connect(self.stop_scan)
        self.btn_stop.setEnabled(False)
        action_row.addWidget(self.btn_stop)
        
        self.btn_save_vault = QPushButton("Save Results to DeviceVault")
        self.btn_save_vault.setStyleSheet(Theme.success_btn_style())
        self.btn_save_vault.clicked.connect(self.save_to_devicevault)
        self.btn_save_vault.setEnabled(False)
        action_row.addWidget(self.btn_save_vault)
        action_row.addStretch()

        controls_vbox.addLayout(action_row)
        main_layout.addWidget(controls_frame)
        
        # Known Devices (Phase 11A - compact table from DeviceVault, safe single-IP recheck only)
        known_frame = QFrame()
        known_frame.setStyleSheet(Theme.section_frame_style())
        known_frame.setMaximumHeight(280)
        known_layout = QVBoxLayout(known_frame)
        
        known_title = QLabel("KNOWN DEVICES")
        known_title.setStyleSheet(Theme.section_title_style())
        known_layout.addWidget(known_title)
        
        self.known_devices_table = QTableWidget(0, 9)
        self.known_devices_table.setHorizontalHeaderLabels([
            "Name", "IP Address", "MAC Address", "Vendor", "Device Type", "Last Known Status", "Last Seen", "Current Status", "Change"
        ])
        self.known_devices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.known_devices_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.known_devices_table.setStyleSheet(Theme.compact_table_style())
        self.known_devices_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.known_devices_table.setSelectionMode(QTableWidget.SingleSelection)
        self.known_devices_table.setAlternatingRowColors(True)
        self.known_devices_table.itemSelectionChanged.connect(self.on_known_device_selected)
        known_layout.addWidget(self.known_devices_table)
        
        known_btn_layout = QHBoxLayout()
        self.btn_load_known = QPushButton("Load Known Devices")
        self.btn_load_known.setStyleSheet(Theme.secondary_btn_style())
        self.btn_load_known.clicked.connect(self.load_known_devices)
        known_btn_layout.addWidget(self.btn_load_known)
        
        self.btn_recheck_selected_device = QPushButton("Recheck Selected Device")
        self.btn_recheck_selected_device.setStyleSheet(Theme.secondary_btn_style())
        self.btn_recheck_selected_device.clicked.connect(self.recheck_selected_device)
        known_btn_layout.addWidget(self.btn_recheck_selected_device)
        
        self.btn_recheck_all_known = QPushButton("Recheck All Known Devices")
        self.btn_recheck_all_known.setStyleSheet(Theme.secondary_btn_style())
        self.btn_recheck_all_known.clicked.connect(self.recheck_all_known_devices)
        known_btn_layout.addWidget(self.btn_recheck_all_known)
        known_btn_layout.addStretch()
        
        known_layout.addLayout(known_btn_layout)
        main_layout.addWidget(known_frame)
        
        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(Theme.status_label_style())
        main_layout.addWidget(self.status_label)
        
        # Content Splitter (Table + Details)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        
        # Results Table
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Status", "IP Address", "Name", "MAC Address", "Vendor", "Response Time", "Last Seen"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # Status
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # IP Address
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # Name
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # MAC Address
        header.setSectionResizeMode(4, QHeaderView.Stretch)          # Vendor
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Response Time
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Last Seen
        
        self.table.setStyleSheet(Theme.table_style())
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_table_selection)
        
        splitter.addWidget(self.table)
        
        # Details Panel
        self.details_panel = QFrame()
        self.details_panel.setStyleSheet(Theme.details_panel_style())
        self.details_layout = QVBoxLayout(self.details_panel)
        self.details_layout.setAlignment(Qt.AlignTop)
        
        panel_title = QLabel("Device Details")
        panel_title.setStyleSheet(Theme.panel_title_style())
        self.details_layout.addWidget(panel_title)
        
        self.details_labels = {}
        fields = [
            "IP Address", "Name", "Detected Hostname", "MAC Address", "Vendor", "Device Type", 
            "Discovery Source", "Confidence", "Manual Override", "Vendor Override", "Response Time", "Last Seen", "Notes"
        ]
        
        for f in fields:
            lbl = QLabel(f"<b>{f}:</b> —")
            lbl.setStyleSheet(Theme.detail_label_style())
            lbl.setWordWrap(True)
            self.details_layout.addWidget(lbl)
            self.details_labels[f] = lbl
            
        splitter.addWidget(self.details_panel)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)
        
        main_layout.addWidget(splitter)
        
        self.scanner_thread = None

    def start_scan(self):
        subnet_str = self.subnet_input.text().strip()
        
        try:
            network = ipaddress.ip_network(subnet_str, strict=False)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid CIDR subnet, e.g. 192.168.1.0/24")
            return
            
        logger.info(f"Starting IPHawk scan on {subnet_str}")
        
        self.is_cancelled = False
        self.host_data_map.clear()
        self.table.setRowCount(0)
        self.clear_details_panel()
        
        self.btn_start.setEnabled(False)
        self.subnet_input.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status_label.setText(f"Scanning {subnet_str}...")
        
        self.scanner_thread = ScannerThread(subnet_str)
        self.scanner_thread.host_found.connect(self.add_host_to_table)
        self.scanner_thread.mac_resolved.connect(self.update_mac)
        self.scanner_thread.scan_finished.connect(self.on_scan_finished)
        self.scanner_thread.progress_update.connect(self.update_progress)
        self.scanner_thread.start()

    def stop_scan(self):
        if self.scanner_thread and self.scanner_thread.isRunning():
            logger.info("Stopping IPHawk scan...")
            self.is_cancelled = True
            self.status_label.setText("Stopping scan...")
            self.btn_stop.setEnabled(False)
            self.scanner_thread.stop()

    @Slot(dict)
    def add_host_to_table(self, host_data):
        if getattr(self, 'is_cancelled', False):
            return
            
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        self.host_data_map[host_data['ip']] = host_data
        
        status_item = QTableWidgetItem("Online")
        status_item.setForeground(Qt.green)
        self.table.setItem(row, 0, status_item)
        
        ip_item = QTableWidgetItem(host_data.get('ip', ''))
        self.table.setItem(row, 1, ip_item)
        
        name = host_data.get('display_name', '—')
        name_item = QTableWidgetItem(name)
        if name != "—":
            name_item.setToolTip(name)
            conf = host_data.get('confidence', 'Low')
            if conf == "High":
                name_item.setForeground(Qt.green)
            elif conf == "Medium":
                name_item.setForeground(Qt.yellow)
        else:
            name_item.setForeground(Qt.gray)
            
        self.table.setItem(row, 2, name_item)
        
        mac = host_data.get('mac') or '—'
        mac_item = QTableWidgetItem(mac)
        if mac == '—': mac_item.setForeground(Qt.gray)
        self.table.setItem(row, 3, mac_item)
        
        vo = host_data.get('vendor_override')
        vendor = vo if vo else (host_data.get('vendor') or '—')
        if vendor == "Unknown": vendor = "—"
        vendor_item = QTableWidgetItem(vendor)
        vendor_item.setToolTip(vendor)
        if vendor == '—': vendor_item.setForeground(Qt.gray)
        self.table.setItem(row, 4, vendor_item)
        
        self.table.setItem(row, 5, QTableWidgetItem(f"{host_data.get('response_time', 0)} ms"))
        self.table.setItem(row, 6, QTableWidgetItem(host_data.get('last_seen', '')))

    @Slot(str, str, str)
    def update_mac(self, ip, mac, vendor):
        if getattr(self, 'is_cancelled', False):
            return
            
        if ip in self.host_data_map:
            hd = self.host_data_map[ip]
            hd['mac'] = mac
            hd['vendor'] = vendor
            
            for row in range(self.table.rowCount()):
                if self.table.item(row, 1).text() == ip:
                    mac_item = self.table.item(row, 3)
                    mac_item.setText(mac)
                    if mac == '—' or mac == 'Pending...':
                        mac_item.setForeground(Qt.gray)
                    else:
                        mac_item.setData(Qt.ForegroundRole, None)
                    
                    vo = hd.get('vendor_override', '')
                    final_vendor = vo if vo else (vendor if vendor and vendor != "Unknown" else "—")
                    vend_item = self.table.item(row, 4)
                    vend_item.setText(final_vendor)
                    vend_item.setToolTip(final_vendor)
                    if final_vendor == '—':
                        vend_item.setForeground(Qt.gray)
                    else:
                        vend_item.setData(Qt.ForegroundRole, None)
                    break
                    
            self.refresh_details_if_selected(ip)

    @Slot()
    def on_table_selection(self):
        selected = self.table.selectedItems()
        if not selected:
            self.clear_details_panel()
            return
            
        row = selected[0].row()
        ip = self.table.item(row, 1).text()
        hd = self.host_data_map.get(ip)
        if hd:
            self.update_details_panel(hd)

    def update_details_panel(self, hd):
        self.details_labels["IP Address"].setText(f"<b>IP Address:</b> {hd.get('ip') or '—'}")
        self.details_labels["Name"].setText(f"<b>Name:</b> {hd.get('display_name') or '—'}")
        self.details_labels["Detected Hostname"].setText(f"<b>Detected Hostname:</b> {hd.get('hostname') or '—'}")
        self.details_labels["MAC Address"].setText(f"<b>MAC Address:</b> {hd.get('mac') or '—'}")
        
        vo = hd.get('vendor_override')
        vendor = hd.get('vendor')
        if vendor == "Unknown": vendor = "—"
        final_vendor = vo if vo else (vendor or '—')
        self.details_labels["Vendor"].setText(f"<b>Vendor:</b> {final_vendor}")
        
        self.details_labels["Device Type"].setText(f"<b>Device Type:</b> {hd.get('device_type') or 'Unclassified'}")
        self.details_labels["Discovery Source"].setText(f"<b>Discovery Source:</b> {hd.get('source') or '—'}")
        
        conf = hd.get('confidence') or '—'
        color = Theme.COLORS.TEXT
        if conf == "High": color = Theme.COLORS.SUCCESS
        elif conf == "Medium": color = Theme.COLORS.WARNING
        elif conf == "Low": color = Theme.COLORS.DANGER
        self.details_labels["Confidence"].setText(f"<b>Confidence:</b> <span style='color:{color};'>{conf}</span>")
        
        self.details_labels["Manual Override"].setText(f"<b>Manual Override:</b> {hd.get('manual_override') or 'No'}")
        self.details_labels["Vendor Override"].setText(f"<b>Vendor Override:</b> {hd.get('vendor_over_applied') or 'No'}")
        self.details_labels["Response Time"].setText(f"<b>Response Time:</b> {hd.get('response_time', 0)} ms")
        self.details_labels["Last Seen"].setText(f"<b>Last Seen:</b> {hd.get('last_seen') or '—'}")
        
        notes = hd.get('notes')
        self.details_labels["Notes"].setText(f"<b>Notes:</b> {notes if notes else '—'}")

    def clear_details_panel(self):
        for f, lbl in self.details_labels.items():
            lbl.setText(f"<b>{f}:</b> —")

    def refresh_details_if_selected(self, ip):
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            sel_ip = self.table.item(row, 1).text()
            if sel_ip == ip:
                hd = self.host_data_map.get(ip)
                if hd:
                    self.update_details_panel(hd)

    @Slot(str)
    def update_progress(self, msg):
        if not getattr(self, 'is_cancelled', False):
            self.status_label.setText(msg)

    @Slot()
    def save_to_devicevault(self):
        if not self.host_data_map:
            QMessageBox.information(self, "No Data", "There are no scan results to save.")
            return
            
        db = SessionLocal()
        try:
            results = list(self.host_data_map.values())
            success, saved, updated = DeviceVaultService.save_scan_results(db, results)
            
            if success:
                QMessageBox.information(self, "DeviceVault Sync", f"Successfully synced to DeviceVault.\n\nAdded: {saved}\nUpdated: {updated}")
            else:
                QMessageBox.warning(self, "Error", "Failed to sync with DeviceVault. Check logs.")
        finally:
            db.close()

    @Slot()
    def on_scan_finished(self):
        logger.info("IPHawk scan finished.")
        if getattr(self, 'is_cancelled', False):
            self.status_label.setText("Scan stopped by user.")
        else:
            self.status_label.setText("Scan complete.")
        self.btn_start.setEnabled(True)
        self.subnet_input.setEnabled(True)
        self.btn_stop.setEnabled(False)
        if self.host_data_map:
            self.btn_save_vault.setEnabled(True)

    def load_known_devices(self):
        """Load known devices from DeviceVault into known_devices_table."""
        db = SessionLocal()
        try:
            summary = DeviceVaultService.get_known_devices_summary(db)
            self.known_devices_table.setRowCount(0)
            for item in summary:
                row = self.known_devices_table.rowCount()
                self.known_devices_table.insertRow(row)
                self.known_devices_table.setItem(row, 0, QTableWidgetItem(item['name']))
                self.known_devices_table.setItem(row, 1, QTableWidgetItem(item['ip_address']))
                self.known_devices_table.setItem(row, 2, QTableWidgetItem(item['mac_address']))
                self.known_devices_table.setItem(row, 3, QTableWidgetItem(item['vendor']))
                self.known_devices_table.setItem(row, 4, QTableWidgetItem(item['device_type']))
                self.known_devices_table.setItem(row, 5, QTableWidgetItem(item['status']))
                self.known_devices_table.setItem(row, 6, QTableWidgetItem(item['last_seen']))
                self.known_devices_table.setItem(row, 7, QTableWidgetItem("—"))  # Current Status
                self.known_devices_table.setItem(row, 8, QTableWidgetItem("Unknown"))  # Change
            if not summary:
                self.known_devices_table.setRowCount(1)
                no_data_item = QTableWidgetItem("No known devices found. Run IPHawk scan and save results to DeviceVault.")
                no_data_item.setTextAlignment(Qt.AlignCenter)
                self.known_devices_table.setItem(0, 0, no_data_item)
                self.known_devices_table.setSpan(0, 0, 1, 9)
        finally:
            db.close()

    def on_known_device_selected(self):
        """Populate target when a known device row is selected (no auto-scan)."""
        selected = self.known_devices_table.selectedItems()
        if selected:
            ip = self.known_devices_table.item(selected[0].row(), 1).text()
            if ip and ip != "—":
                self.subnet_input.setText(ip)

    def recheck_selected_device(self):
        """Recheck only the selected known device IP using existing safe logic (no full subnet)."""
        selected = self.known_devices_table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "No known device selected.")
            return
        row = selected[0].row()
        ip = self.known_devices_table.item(row, 1).text()
        if ip and ip != "—":
            self.subnet_input.setText(ip)
            self.start_scan()  # Reuse existing safe IP check for the single IP

    def recheck_all_known_devices(self):
        """Recheck all loaded known devices (user-triggered, reuses existing safety; no subnet expansion)."""
        db = SessionLocal()
        try:
            summary = DeviceVaultService.get_known_devices_summary(db)
            if not summary:
                QMessageBox.information(self, "No Data", "No known devices to recheck.")
                return
            for item in summary:
                ip = item['ip_address']
                if ip and ip != "—":
                    self.subnet_input.setText(ip)
                    self.start_scan()
            QMessageBox.information(self, "Recheck Initiated", "Recheck of known devices started using existing safe logic.")
        finally:
            db.close()

    def detect_network(self):
        """Auto-detect local IPv4 network and pre-fill subnet input. No scan triggered."""
        cidr, local_ip, interface = self._detect_local_ipv4_network()
        if cidr:
            self.subnet_input.setText(cidr)
            self.detected_label.setText(f"Detected local network: {cidr} via {interface or 'LAN'} (local IP: {local_ip})")
            logger.info(f"Auto-detected local network: {cidr} (IP: {local_ip})")
        else:
            self.detected_label.setText("Could not auto-detect local network. Please enter subnet manually.")
            logger.warning("Local network detection failed.")

    def _detect_local_ipv4_network(self):
        """Safe best-effort local IPv4 network detection using stdlib only. No network calls."""
        try:
            # Get local IP by connecting to a public DNS (does not send data)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Determine CIDR based on private range (safe assumption for home/lab networks)
            if local_ip.startswith('10.'):
                cidr = local_ip.rsplit('.', 1)[0] + '.0/24'
            elif local_ip.startswith('172.'):
                cidr = local_ip.rsplit('.', 2)[0] + '.0/16'
            elif local_ip.startswith('192.168.'):
                cidr = local_ip.rsplit('.', 1)[0] + '.0/24'
            else:
                cidr = local_ip.rsplit('.', 1)[0] + '.0/24'
            
            interface = "LAN"
            if local_ip.startswith('127.'):
                interface = "Loopback"
            elif local_ip.startswith('169.254.'):
                interface = "APIPA"
            
            return cidr, local_ip, interface
        except Exception as e:
            logger.error(f"Network detection error: {e}")
            return None, None, None
