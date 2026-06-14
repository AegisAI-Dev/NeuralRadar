from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QSplitter,
    QTextEdit, QComboBox
)
from PySide6.QtCore import Qt, Slot
from app.core.database import SessionLocal
from app.modules.devicevault.service import DeviceVaultService
from app.core.logger import logger

class DeviceVaultPage(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("DeviceVault")
        title.setStyleSheet("color: #cdd6f4; font-size: 28px; font-weight: bold;")
        subtitle = QLabel("Persistent local network asset inventory")
        subtitle.setStyleSheet("color: #89b4fa; font-size: 14px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
        notice_label = QLabel("ℹ️ Device inventory is stored locally on this machine.")
        notice_label.setStyleSheet("color: #a6e3a1; font-size: 13px; font-weight: bold; background-color: #313244; padding: 10px; border-radius: 6px;")
        main_layout.addWidget(notice_label)
        
        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by IP, Name, MAC, Vendor, Tags...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 4px;
                padding: 10px;
                font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #89b4fa; }
        """)
        self.search_input.textChanged.connect(self.load_devices)
        search_layout.addWidget(self.search_input)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #b4befe; }
        """)
        self.btn_refresh.clicked.connect(self.load_devices)
        search_layout.addWidget(self.btn_refresh)
        
        main_layout.addLayout(search_layout)
        
        # Content Splitter (Table + Edit Details)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        splitter.setStyleSheet("QSplitter::handle { background-color: transparent; }")
        
        # Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Status", "IP Address", "Name", "MAC Address", "Vendor", "Device Type", "Last Seen"
        ])
        self.table.hideColumn(0) # Hide ID column
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
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
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        splitter.addWidget(self.table)
        
        # Details Panel
        self.details_panel = QFrame()
        self.details_panel.setStyleSheet("QFrame { background-color: #1e1e2e; border: 1px solid #313244; border-radius: 4px; }")
        self.details_layout = QVBoxLayout(self.details_panel)
        self.details_layout.setAlignment(Qt.AlignTop)
        
        panel_title = QLabel("Device Details & Edit")
        panel_title.setStyleSheet("color: #cdd6f4; font-size: 16px; font-weight: bold; border: none; padding-bottom: 10px;")
        self.details_layout.addWidget(panel_title)
        
        # Read-only fields
        self.lbl_ip = QLabel("IP Address: —")
        self.lbl_mac = QLabel("MAC Address: —")
        self.lbl_vendor = QLabel("Vendor: —")
        self.lbl_detected_host = QLabel("Detected Hostname: —")
        self.lbl_source = QLabel("Discovery Source: —")
        self.lbl_confidence = QLabel("Confidence: —")
        self.lbl_first_seen = QLabel("First Seen: —")
        self.lbl_last_seen = QLabel("Last Seen: —")
        
        for lbl in [self.lbl_ip, self.lbl_mac, self.lbl_vendor, self.lbl_detected_host, self.lbl_source, self.lbl_confidence, self.lbl_first_seen, self.lbl_last_seen]:
            lbl.setStyleSheet("color: #a6adc8; font-size: 13px; border: none;")
            lbl.setWordWrap(True)
            self.details_layout.addWidget(lbl)
            
        self.details_layout.addSpacing(10)
        
        # Editable fields
        self.lbl_name_edit = QLabel("Custom Name:")
        self.lbl_name_edit.setStyleSheet("color: #cdd6f4; font-weight: bold; border: none;")
        self.details_layout.addWidget(self.lbl_name_edit)
        self.edit_name = QLineEdit()
        self.edit_name.setStyleSheet("background-color: #181825; color: #cdd6f4; border: 1px solid #313244; padding: 5px; border-radius: 4px;")
        self.details_layout.addWidget(self.edit_name)
        
        self.lbl_type_edit = QLabel("Device Type:")
        self.lbl_type_edit.setStyleSheet("color: #cdd6f4; font-weight: bold; border: none;")
        self.details_layout.addWidget(self.lbl_type_edit)
        self.edit_type = QComboBox()
        self.edit_type.addItems([
            "Unclassified", "Router", "Switch", "Firewall", "NAS", "Server", "Workstation", 
            "Laptop", "Virtual Machine", "Container", "IoT Device", "Printer", "Mobile Device", "Other"
        ])
        self.edit_type.setStyleSheet("background-color: #181825; color: #cdd6f4; border: 1px solid #313244; padding: 5px; border-radius: 4px;")
        self.details_layout.addWidget(self.edit_type)
        
        self.lbl_tags_edit = QLabel("Tags (comma separated):")
        self.lbl_tags_edit.setStyleSheet("color: #cdd6f4; font-weight: bold; border: none;")
        self.details_layout.addWidget(self.lbl_tags_edit)
        self.edit_tags = QLineEdit()
        self.edit_tags.setStyleSheet("background-color: #181825; color: #cdd6f4; border: 1px solid #313244; padding: 5px; border-radius: 4px;")
        self.details_layout.addWidget(self.edit_tags)
        
        self.lbl_notes_edit = QLabel("Notes:")
        self.lbl_notes_edit.setStyleSheet("color: #cdd6f4; font-weight: bold; border: none;")
        self.details_layout.addWidget(self.lbl_notes_edit)
        self.edit_notes = QTextEdit()
        self.edit_notes.setMaximumHeight(80)
        self.edit_notes.setStyleSheet("background-color: #181825; color: #cdd6f4; border: 1px solid #313244; padding: 5px; border-radius: 4px;")
        self.details_layout.addWidget(self.edit_notes)
        
        self.btn_save_changes = QPushButton("Save Changes")
        self.btn_save_changes.setStyleSheet("""
            QPushButton { background-color: #a6e3a1; color: #11111b; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:hover { background-color: #94e2d5; }
            QPushButton:disabled { background-color: #313244; color: #6c7086; }
        """)
        self.btn_save_changes.clicked.connect(self.save_manual_edits)
        self.btn_save_changes.setEnabled(False)
        self.details_layout.addWidget(self.btn_save_changes)
        
        splitter.addWidget(self.details_panel)
        splitter.setStretchFactor(0, 7)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        
        self.current_device_id = None
        
    def showEvent(self, event):
        super().showEvent(event)
        self.load_devices()

    def load_devices(self):
        query = self.search_input.text().strip()
        db = SessionLocal()
        try:
            if query:
                devices = DeviceVaultService.search_devices(db, query)
            else:
                devices = DeviceVaultService.get_all_devices(db)
                
            self.table.setRowCount(0)
            for d in devices:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # Hidden ID
                self.table.setItem(row, 0, QTableWidgetItem(str(d.id)))
                
                # Status
                status_item = QTableWidgetItem(d.status)
                if d.status == "Online": status_item.setForeground(Qt.green)
                else: status_item.setForeground(Qt.gray)
                self.table.setItem(row, 1, status_item)
                
                self.table.setItem(row, 2, QTableWidgetItem(d.ip_address))
                self.table.setItem(row, 3, QTableWidgetItem(d.name))
                self.table.setItem(row, 4, QTableWidgetItem(d.mac_address))
                self.table.setItem(row, 5, QTableWidgetItem(d.vendor))
                self.table.setItem(row, 6, QTableWidgetItem(d.device_type))
                self.table.setItem(row, 7, QTableWidgetItem(d.last_seen))
                
                # Store full device data in row for details panel
                self.table.item(row, 0).setData(Qt.UserRole, {
                    "detected_hostname": d.detected_hostname,
                    "discovery_source": d.discovery_source,
                    "confidence": d.confidence,
                    "first_seen": d.first_seen,
                    "tags": d.tags,
                    "notes": d.notes
                })
        finally:
            db.close()
            
    @Slot()
    def on_selection_changed(self):
        selected = self.table.selectedItems()
        if not selected:
            self.current_device_id = None
            self.btn_save_changes.setEnabled(False)
            return
            
        row = selected[0].row()
        self.current_device_id = int(self.table.item(row, 0).text())
        ip = self.table.item(row, 2).text()
        name = self.table.item(row, 3).text()
        mac = self.table.item(row, 4).text()
        vendor = self.table.item(row, 5).text()
        dev_type = self.table.item(row, 6).text()
        last_seen = self.table.item(row, 7).text()
        
        extra_data = self.table.item(row, 0).data(Qt.UserRole)
        
        self.lbl_ip.setText(f"<b>IP Address:</b> {ip}")
        self.lbl_mac.setText(f"<b>MAC Address:</b> {mac}")
        self.lbl_vendor.setText(f"<b>Vendor:</b> {vendor}")
        self.lbl_detected_host.setText(f"<b>Detected Hostname:</b> {extra_data['detected_hostname']}")
        self.lbl_source.setText(f"<b>Discovery Source:</b> {extra_data['discovery_source']}")
        self.lbl_confidence.setText(f"<b>Confidence:</b> {extra_data['confidence']}")
        self.lbl_first_seen.setText(f"<b>First Seen:</b> {extra_data['first_seen']}")
        self.lbl_last_seen.setText(f"<b>Last Seen:</b> {last_seen}")
        
        self.edit_name.setText(name if name != "—" else "")
        index = self.edit_type.findText(dev_type)
        if index >= 0: self.edit_type.setCurrentIndex(index)
        else: self.edit_type.setCurrentIndex(0)
        self.edit_tags.setText(extra_data['tags'])
        self.edit_notes.setPlainText(extra_data['notes'])
        
        self.btn_save_changes.setEnabled(True)

    @Slot()
    def save_manual_edits(self):
        if not self.current_device_id: return
        
        name = self.edit_name.text().strip() or "—"
        dev_type = self.edit_type.currentText()
        tags = self.edit_tags.text().strip()
        notes = self.edit_notes.toPlainText().strip()
        
        db = SessionLocal()
        try:
            success = DeviceVaultService.update_manual_fields(db, self.current_device_id, name, dev_type, tags, notes)
            if success:
                QMessageBox.information(self, "Success", "Device details updated successfully.")
                self.load_devices()
            else:
                QMessageBox.warning(self, "Error", "Failed to update device details.")
        finally:
            db.close()
