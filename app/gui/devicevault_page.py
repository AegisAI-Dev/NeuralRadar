from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QSplitter,
    QTextEdit, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt, Slot
from app.core.database import SessionLocal
from app.modules.devicevault.service import DeviceVaultService
from app.modules.devicevault.exporter import (
    export_devices_csv, 
    export_devices_json, 
    export_full_inventory_json
)
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

        # Export buttons (minimal addition)
        export_layout = QHBoxLayout()
        export_label = QLabel("Export:")
        export_label.setStyleSheet("color: #94A3B8; font-size: 13px;")
        export_layout.addWidget(export_label)
        
        self.btn_export_csv = QPushButton("Devices CSV")
        self.btn_export_csv.clicked.connect(self.export_devices_to_csv)
        export_layout.addWidget(self.btn_export_csv)
        
        self.btn_export_json = QPushButton("Devices JSON")
        self.btn_export_json.clicked.connect(self.export_devices_to_json)
        export_layout.addWidget(self.btn_export_json)
        
        self.btn_export_full = QPushButton("Full Inventory JSON")
        self.btn_export_full.clicked.connect(self.export_full_inventory)
        export_layout.addWidget(self.btn_export_full)
        
        export_layout.addStretch()
        main_layout.addLayout(export_layout)
        
        # Content Splitter (Table + Edit Details)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        splitter.setStyleSheet("QSplitter::handle { background-color: transparent; }")
        
        # Table Container
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_empty_state = QLabel("No devices saved yet. Run an IPHawk scan and save results to DeviceVault.")
        self.lbl_empty_state.setAlignment(Qt.AlignCenter)
        self.lbl_empty_state.setStyleSheet("color: #a6adc8; font-size: 16px; font-style: italic; background-color: #1e1e2e; border: 1px solid #313244; border-radius: 4px;")
        self.lbl_empty_state.hide()
        self.table_layout.addWidget(self.lbl_empty_state)
        
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
        
        self.table_layout.addWidget(self.table)
        splitter.addWidget(self.table_container)
        
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
        
        self.details_layout.addSpacing(15)
        
        # Open Services Section
        services_title = QLabel("Open Services")
        services_title.setStyleSheet("color: #cdd6f4; font-size: 14px; font-weight: bold; border: none; padding-bottom: 5px;")
        self.details_layout.addWidget(services_title)
        
        self.lbl_no_services = QLabel("No services saved yet.")
        self.lbl_no_services.setStyleSheet("color: #6c7086; font-style: italic; border: none;")
        self.details_layout.addWidget(self.lbl_no_services)
        
        self.services_table = QTableWidget(0, 5)
        self.services_table.setHorizontalHeaderLabels(["Port", "Protocol", "Service", "State", "Last Seen"])
        self.services_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.services_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.services_table.setStyleSheet("""
            QTableWidget { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; gridline-color: #313244; outline: none; }
            QHeaderView::section { background-color: #313244; color: #cdd6f4; padding: 4px; border: none; font-weight: bold; font-size: 11px; }
            QTableWidget::item { padding: 4px; font-size: 11px; outline: none; }
        """)
        self.services_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.services_table.setSelectionMode(QTableWidget.NoSelection)
        self.services_table.verticalHeader().setVisible(False)
        self.services_table.setMaximumHeight(150)
        self.services_table.hide()
        self.details_layout.addWidget(self.services_table)
        
        # Web Metadata Section
        web_title = QLabel("Web Metadata")
        web_title.setStyleSheet("color: #cdd6f4; font-size: 14px; font-weight: bold; border: none; padding-top: 10px; padding-bottom: 5px;")
        self.details_layout.addWidget(web_title)
        
        self.lbl_no_web = QLabel("No web metadata saved yet. Run WebPulse and save results.")
        self.lbl_no_web.setStyleSheet("color: #6c7086; font-style: italic; border: none;")
        self.details_layout.addWidget(self.lbl_no_web)
        
        self.web_table = QTableWidget(0, 7)
        self.web_table.setHorizontalHeaderLabels(["URL", "Status", "HTTP Code", "Title", "Server", "SSL Expiry", "Last Checked"])
        self.web_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.web_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.web_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.web_table.setStyleSheet("""
            QTableWidget { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 4px; gridline-color: #313244; outline: none; }
            QHeaderView::section { background-color: #313244; color: #cdd6f4; padding: 4px; border: none; font-weight: bold; font-size: 11px; }
            QTableWidget::item { padding: 4px; font-size: 11px; outline: none; }
        """)
        self.web_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.web_table.setSelectionMode(QTableWidget.NoSelection)
        self.web_table.verticalHeader().setVisible(False)
        self.web_table.setMaximumHeight(150)
        self.web_table.hide()
        self.details_layout.addWidget(self.web_table)
        
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
            
            if not devices and not query:
                self.table.hide()
                self.lbl_empty_state.show()
                self.details_panel.hide()
            else:
                self.table.show()
                self.lbl_empty_state.hide()
                self.details_panel.show()
                
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
        
        # Load services
        db = SessionLocal()
        try:
            services = DeviceVaultService.get_device_services(db, self.current_device_id)
            if services:
                self.lbl_no_services.hide()
                self.services_table.show()
                self.services_table.setRowCount(0)
                for srv in services:
                    r = self.services_table.rowCount()
                    self.services_table.insertRow(r)
                    self.services_table.setItem(r, 0, QTableWidgetItem(str(srv.port)))
                    self.services_table.setItem(r, 1, QTableWidgetItem(srv.protocol))
                    self.services_table.setItem(r, 2, QTableWidgetItem(srv.service_guess))
                    state_item = QTableWidgetItem(srv.state)
                    state_item.setForeground(Qt.green)
                    self.services_table.setItem(r, 3, state_item)
                    self.services_table.setItem(r, 4, QTableWidgetItem(srv.last_seen))
            else:
                self.services_table.hide()
                self.lbl_no_services.show()
                
            # Load web services
            try:
                web_services = DeviceVaultService.get_device_web_services(db, self.current_device_id)
                if web_services:
                    self.lbl_no_web.hide()
                    self.web_table.show()
                    self.web_table.setRowCount(0)
                    for ws in web_services:
                        r = self.web_table.rowCount()
                        self.web_table.insertRow(r)
                        self.web_table.setItem(r, 0, QTableWidgetItem(ws.url))
                        
                        status_item = QTableWidgetItem(ws.status)
                        if ws.status == "Online": status_item.setForeground(Qt.green)
                        elif ws.status == "Redirect Warning": status_item.setForeground(Qt.yellow)
                        elif ws.status == "TLS Warning": status_item.setForeground(Qt.darkYellow)
                        elif ws.status == "Protocol Mismatch": status_item.setForeground(Qt.cyan)
                        elif ws.status == "TLS/SNI Error": status_item.setForeground(Qt.magenta)
                        else: status_item.setForeground(Qt.red)
                        self.web_table.setItem(r, 1, status_item)
                        
                        self.web_table.setItem(r, 2, QTableWidgetItem(ws.http_code))
                        
                        title_item = QTableWidgetItem(ws.page_title)
                        if ws.page_title == "—": title_item.setForeground(Qt.gray)
                        self.web_table.setItem(r, 3, title_item)
                        
                        server_item = QTableWidgetItem(ws.server_header)
                        if ws.server_header == "—": server_item.setForeground(Qt.gray)
                        self.web_table.setItem(r, 4, server_item)
                        
                        expiry_item = QTableWidgetItem(ws.ssl_expiry)
                        if ws.ssl_expiry == "—": expiry_item.setForeground(Qt.gray)
                        self.web_table.setItem(r, 5, expiry_item)
                        
                        self.web_table.setItem(r, 6, QTableWidgetItem(ws.last_checked))
                else:
                    self.web_table.hide()
                    self.lbl_no_web.show()
            except Exception as e:
                logger.error(f"Error loading web services: {e}")
                
        finally:
            db.close()

    @Slot()

    def _show_export_success(self, path: str):
        QMessageBox.information(self, "Export Successful", f"Data exported to:
{path}")
    
    def _show_no_data(self):
        QMessageBox.information(self, "No Data", "No data available to export.")
    
    def _show_export_error(self, error: str):
        QMessageBox.warning(self, "Export Failed", f"Export failed: {error}")
        logger.error(f"Export error: {error}")
    
    @Slot()
    def export_devices_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Devices CSV", "devices.csv", "CSV Files (*.csv);;All Files (*)"
        )
        if not path:
            return
        if not path.endswith(".csv"):
            path += ".csv"
        if export_devices_csv(path):
            self._show_export_success(path)
        else:
            self._show_no_data()
    
    @Slot()
    def export_devices_to_json(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Devices JSON", "devices.json", "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"
        if export_devices_json(path):
            self._show_export_success(path)
        else:
            self._show_no_data()
    
    @Slot()
    def export_full_inventory(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Full Inventory JSON", "inventory.json", "JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"
        if export_full_inventory_json(path):
            self._show_export_success(path)
        else:
            self._show_no_data()

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
