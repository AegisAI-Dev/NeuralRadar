from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QSplitter
)
from PySide6.QtCore import Qt, Slot
from app.modules.iphawk.scanner import ScannerThread
from app.modules.devicevault.service import DeviceVaultService
from app.core.database import SessionLocal
from app.core.logger import logger
import ipaddress

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
        title.setStyleSheet("color: #cdd6f4; font-size: 28px; font-weight: bold;")
        subtitle = QLabel("Local network discovery module")
        subtitle.setStyleSheet("color: #89b4fa; font-size: 14px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
        # Security Notice
        notice_label = QLabel("⚠️ Only scan networks you own or have permission to test.")
        notice_label.setStyleSheet("color: #f38ba8; font-size: 13px; font-weight: bold; background-color: #313244; padding: 10px; border-radius: 6px;")
        main_layout.addWidget(notice_label)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.subnet_input = QLineEdit()
        self.subnet_input.setPlaceholderText("e.g. 192.168.1.0/24")
        self.subnet_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }
        """)
        controls_layout.addWidget(self.subnet_input)
        
        self.btn_start = QPushButton("Start Scan")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
            QPushButton:disabled {
                background-color: #313244;
                color: #6c7086;
            }
        """)
        self.btn_start.clicked.connect(self.start_scan)
        controls_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("Stop Scan")
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #f38ba8;
                color: #11111b;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #eba0ac;
            }
            QPushButton:disabled {
                background-color: #313244;
                color: #6c7086;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_scan)
        self.btn_stop.setEnabled(False)
        controls_layout.addWidget(self.btn_stop)
        
        self.btn_save_vault = QPushButton("Save to DeviceVault")
        self.btn_save_vault.setStyleSheet("""
            QPushButton {
                background-color: #a6e3a1;
                color: #11111b;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #94e2d5;
            }
            QPushButton:disabled {
                background-color: #313244;
                color: #6c7086;
            }
        """)
        self.btn_save_vault.clicked.connect(self.save_to_devicevault)
        self.btn_save_vault.setEnabled(False)
        controls_layout.addWidget(self.btn_save_vault)
        
        main_layout.addLayout(controls_layout)
        
        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #a6adc8; font-size: 13px;")
        main_layout.addWidget(self.status_label)
        
        # Content Splitter (Table + Details)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
            }
        """)
        
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
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 4px;
                gridline-color: #313244;
                outline: none;
            }
            QTableWidget:focus {
                outline: none;
            }
            QHeaderView::section {
                background-color: #313244;
                color: #cdd6f4;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                outline: none;
            }
            QTableWidget::item:focus {
                outline: none;
            }
            QTableWidget::item:selected {
                background-color: #313244;
                color: #cdd6f4;
                outline: none;
            }
        """)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_table_selection)
        
        splitter.addWidget(self.table)
        
        # Details Panel
        self.details_panel = QFrame()
        self.details_panel.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 4px;
            }
        """)
        self.details_layout = QVBoxLayout(self.details_panel)
        self.details_layout.setAlignment(Qt.AlignTop)
        
        panel_title = QLabel("Device Details")
        panel_title.setStyleSheet("color: #cdd6f4; font-size: 16px; font-weight: bold; border: none; padding-bottom: 10px;")
        self.details_layout.addWidget(panel_title)
        
        self.details_labels = {}
        fields = [
            "IP Address", "Name", "Detected Hostname", "MAC Address", "Vendor", "Device Type", 
            "Discovery Source", "Confidence", "Manual Override", "Vendor Override", "Response Time", "Last Seen", "Notes"
        ]
        
        for f in fields:
            lbl = QLabel(f"<b>{f}:</b> —")
            lbl.setStyleSheet("color: #a6adc8; font-size: 13px; border: none; padding: 4px 0;")
            lbl.setWordWrap(True)
            self.details_layout.addWidget(lbl)
            self.details_labels[f] = lbl
            
        splitter.addWidget(self.details_panel)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        
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
        color = "#cdd6f4"
        if conf == "High": color = "#a6e3a1"
        elif conf == "Medium": color = "#f9e2af"
        elif conf == "Low": color = "#f38ba8"
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
