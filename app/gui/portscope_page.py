from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, Slot
from app.modules.portscope.scanner import PortScannerThread
from app.modules.devicevault.service import DeviceVaultService
from app.core.logger import logger
from app.core.database import SessionLocal
from app.modules.devicevault.models import Device
import ipaddress
import re

PRESETS = {
    "Common Ports": "21,22,23,25,53,80,110,139,143,443,445,587,993,995,3306,3389,5432,5900,8000,8080,8443",
    "Web Ports": "80,443,3000,5000,5173,8000,8080,8443,9000,9443",
    "Admin Ports": "22,80,443,445,3389,5900,8006,8080,8443,9090,9443",
    "Custom": ""
}

class PortScopePage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.is_cancelled = False
        self.scanner_thread = None
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("PortScope")
        title.setStyleSheet("color: #cdd6f4; font-size: 28px; font-weight: bold;")
        subtitle = QLabel("Safe TCP port discovery module")
        subtitle.setStyleSheet("color: #89b4fa; font-size: 14px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
        notice_label = QLabel("⚠️ Only scan systems you own or have permission to test.")
        notice_label.setStyleSheet("color: #f38ba8; font-size: 13px; font-weight: bold; background-color: #313244; padding: 10px; border-radius: 6px;")
        main_layout.addWidget(notice_label)
        
        # Controls Layout
        controls_layout = QHBoxLayout()
        
        # Target Selection
        target_layout = QVBoxLayout()
        lbl_target = QLabel("Target IP:")
        lbl_target.setStyleSheet("color: #cdd6f4; font-weight: bold;")
        self.target_combo = QComboBox()
        self.target_combo.setEditable(True)
        self.target_combo.setPlaceholderText("e.g. 192.168.1.100")
        self.target_combo.setStyleSheet("""
            QComboBox { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; padding: 5px; font-size: 14px; min-width: 200px; }
            QComboBox:focus { border: 1px solid #89b4fa; }
            QComboBox QAbstractItemView { background-color: #1e1e2e; color: #cdd6f4; selection-background-color: #313244; }
        """)
        target_layout.addWidget(lbl_target)
        target_layout.addWidget(self.target_combo)
        controls_layout.addLayout(target_layout)
        
        # Preset Selection
        preset_layout = QVBoxLayout()
        lbl_preset = QLabel("Preset:")
        lbl_preset.setStyleSheet("color: #cdd6f4; font-weight: bold;")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(PRESETS.keys()))
        self.preset_combo.setStyleSheet(self.target_combo.styleSheet())
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(lbl_preset)
        preset_layout.addWidget(self.preset_combo)
        controls_layout.addLayout(preset_layout)
        
        # Ports Input
        ports_layout = QVBoxLayout()
        lbl_ports = QLabel("Ports (e.g. 22,80,443,8000-8100):")
        lbl_ports.setStyleSheet("color: #cdd6f4; font-weight: bold;")
        self.ports_input = QLineEdit()
        self.ports_input.setText(PRESETS["Common Ports"])
        self.ports_input.setStyleSheet("""
            QLineEdit { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; padding: 5px; font-size: 14px; min-width: 300px; }
            QLineEdit:focus { border: 1px solid #89b4fa; }
        """)
        self.ports_input.textEdited.connect(self.on_ports_edited)
        ports_layout.addWidget(lbl_ports)
        ports_layout.addWidget(self.ports_input)
        controls_layout.addLayout(ports_layout)
        
        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setAlignment(Qt.AlignBottom)
        action_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("Start Scan")
        self.btn_start.setStyleSheet("""
            QPushButton { background-color: #89b4fa; color: #11111b; font-weight: bold; padding: 8px 20px; border-radius: 4px; }
            QPushButton:hover { background-color: #b4befe; }
            QPushButton:disabled { background-color: #313244; color: #6c7086; }
        """)
        self.btn_start.clicked.connect(self.start_scan)
        action_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("Stop Scan")
        self.btn_stop.setStyleSheet("""
            QPushButton { background-color: #f38ba8; color: #11111b; font-weight: bold; padding: 8px 20px; border-radius: 4px; }
            QPushButton:hover { background-color: #eba0ac; }
            QPushButton:disabled { background-color: #313244; color: #6c7086; }
        """)
        self.btn_stop.clicked.connect(self.stop_scan)
        self.btn_stop.setEnabled(False)
        action_layout.addWidget(self.btn_stop)
        
        self.btn_save_vault = QPushButton("Save Results to DeviceVault")
        self.btn_save_vault.setStyleSheet("""
            QPushButton { background-color: #a6e3a1; color: #11111b; font-weight: bold; padding: 8px 20px; border-radius: 4px; }
            QPushButton:hover { background-color: #94e2d5; }
            QPushButton:disabled { background-color: #313244; color: #6c7086; }
        """)
        self.btn_save_vault.clicked.connect(self.save_to_devicevault)
        self.btn_save_vault.setEnabled(False)
        action_layout.addWidget(self.btn_save_vault)
        
        btn_layout.addLayout(action_layout)
        controls_layout.addLayout(btn_layout)
        
        main_layout.addLayout(controls_layout)
        
        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #a6adc8; font-size: 13px;")
        main_layout.addWidget(self.status_label)
        
        # Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Status", "Target IP", "Port", "Protocol", "Service Guess", "State", "Response Time", "Last Checked"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        self.table.setStyleSheet("""
            QTableWidget { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; gridline-color: #313244; outline: none; }
            QTableWidget:focus { outline: none; }
            QHeaderView::section { background-color: #313244; color: #cdd6f4; padding: 8px; border: none; font-weight: bold; }
            QTableWidget::item { padding: 8px; outline: none; }
            QTableWidget::item:focus { outline: none; }
            QTableWidget::item:selected { background-color: #313244; color: #cdd6f4; outline: none; }
        """)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        main_layout.addWidget(self.table)
        
        self.load_vault_ips()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_vault_ips()

    def load_vault_ips(self):
        # Refresh combo box with IPs from DeviceVault safely
        current_text = self.target_combo.currentText()
        self.target_combo.clear()
        
        try:
            db = SessionLocal()
            devices = db.query(Device).all()
            for d in devices:
                self.target_combo.addItem(f"{d.ip_address} ({d.name})", d.ip_address)
            db.close()
        except Exception as e:
            logger.error(f"Failed to load DeviceVault IPs: {e}")
            
        if current_text:
            self.target_combo.setCurrentText(current_text)

    @Slot(str)
    def on_preset_changed(self, preset_name):
        if preset_name in PRESETS and PRESETS[preset_name]:
            self.ports_input.setText(PRESETS[preset_name])

    @Slot(str)
    def on_ports_edited(self, text):
        self.preset_combo.setCurrentText("Custom")

    def parse_ports(self, port_str):
        ports = set()
        parts = port_str.split(',')
        for p in parts:
            p = p.strip()
            if not p: continue
            if '-' in p:
                ranges = p.split('-')
                if len(ranges) == 2 and ranges[0].isdigit() and ranges[1].isdigit():
                    start, end = int(ranges[0]), int(ranges[1])
                    if start <= end and start >= 1 and end <= 65535:
                        ports.update(range(start, end + 1))
            elif p.isdigit():
                port = int(p)
                if 1 <= port <= 65535:
                    ports.add(port)
        return sorted(list(ports))

    @Slot()
    def start_scan(self):
        target_text = self.target_combo.currentText().strip()
        # If it's a dropdown item like "192.168.1.1 (Router)", extract just the IP
        if " (" in target_text and target_text.endswith(")"):
            target = target_text.split(" (")[0]
        else:
            target = target_text
            
        if not target:
            QMessageBox.warning(self, "Invalid Target", "Please enter a target IP.")
            return
            
        try:
            ipaddress.ip_address(target)
        except ValueError:
            QMessageBox.warning(self, "Invalid IP", "Please enter a valid IPv4 address.")
            return

        ports_to_scan = self.parse_ports(self.ports_input.text())
        if not ports_to_scan:
            QMessageBox.warning(self, "Invalid Ports", "Please enter valid port numbers (1-65535).")
            return
            
        if len(ports_to_scan) > 10000:
            QMessageBox.warning(self, "Too Many Ports", "Please select 10,000 ports or fewer for safe scanning.")
            return

        logger.info(f"Starting PortScope scan on {target} ({len(ports_to_scan)} ports)")
        
        self.is_cancelled = False
        self.table.setRowCount(0)
        self.btn_start.setEnabled(False)
        self.target_combo.setEnabled(False)
        self.preset_combo.setEnabled(False)
        self.ports_input.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status_label.setText(f"Scanning {target}...")

        self.scanner_thread = PortScannerThread(target, ports_to_scan)
        self.scanner_thread.port_found.connect(self.add_port_to_table)
        self.scanner_thread.progress_update.connect(self.update_progress)
        self.scanner_thread.scan_finished.connect(self.on_scan_finished)
        self.scanner_thread.start()

    @Slot()
    def stop_scan(self):
        if self.scanner_thread and self.scanner_thread.isRunning():
            logger.info("Stopping PortScope scan...")
            self.is_cancelled = True
            self.status_label.setText("Stopping scan...")
            self.btn_stop.setEnabled(False)
            self.scanner_thread.stop()

    @Slot(dict)
    def add_port_to_table(self, result):
        if getattr(self, 'is_cancelled', False):
            return
            
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        status_item = QTableWidgetItem("Online")
        status_item.setForeground(Qt.green)
        self.table.setItem(row, 0, status_item)
        
        self.table.setItem(row, 1, QTableWidgetItem(result['ip']))
        self.table.setItem(row, 2, QTableWidgetItem(str(result['port'])))
        self.table.setItem(row, 3, QTableWidgetItem(result['protocol']))
        
        srv = result['service']
        srv_item = QTableWidgetItem(srv)
        if srv == "—": srv_item.setForeground(Qt.gray)
        self.table.setItem(row, 4, srv_item)
        
        state_item = QTableWidgetItem(result['state'])
        state_item.setForeground(Qt.green)
        self.table.setItem(row, 5, state_item)
        
        self.table.setItem(row, 6, QTableWidgetItem(f"{result['response_time']} ms"))
        self.table.setItem(row, 7, QTableWidgetItem(result['last_checked']))
        
        # Note: In Phase 5, we can sync these discovered ports back to DeviceVault.
        # For now, it simply displays them in the table independently.

    @Slot(str)
    def update_progress(self, msg):
        if not getattr(self, 'is_cancelled', False):
            self.status_label.setText(msg)

    @Slot()
    def save_to_devicevault(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "No Data", "There are no open ports to save.")
            return
            
        results = []
        for row in range(self.table.rowCount()):
            results.append({
                'ip': self.table.item(row, 1).text(),
                'port': int(self.table.item(row, 2).text()),
                'protocol': self.table.item(row, 3).text(),
                'service': self.table.item(row, 4).text(),
                'state': self.table.item(row, 5).text(),
                'response_time': self.table.item(row, 6).text().replace(" ms", ""),
            })
            
        db = SessionLocal()
        try:
            success, saved, updated = DeviceVaultService.save_port_scan_results(db, results)
            
            if success:
                QMessageBox.information(self, "DeviceVault Sync", f"Successfully synced to DeviceVault.\n\nAdded: {saved} ports\nUpdated: {updated} ports")
            else:
                QMessageBox.warning(self, "Error", "Failed to sync with DeviceVault. Check logs.")
        finally:
            db.close()

    @Slot()
    def on_scan_finished(self):
        logger.info("PortScope scan finished.")
        if getattr(self, 'is_cancelled', False):
            self.status_label.setText("Scan stopped by user.")
        else:
            self.status_label.setText("Scan complete.")
            
        self.btn_start.setEnabled(True)
        self.target_combo.setEnabled(True)
        self.preset_combo.setEnabled(True)
        self.ports_input.setEnabled(True)
        self.btn_stop.setEnabled(False)
        if self.table.rowCount() > 0:
            self.btn_save_vault.setEnabled(True)
