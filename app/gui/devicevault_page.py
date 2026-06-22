from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QSplitter,
    QTextEdit, QComboBox, QFileDialog, QInputDialog, QScrollArea
)
from PySide6.QtCore import Qt, Slot
from app.core.database import SessionLocal
from app.modules.devicevault.service import DeviceVaultService
from app.modules.devicevault.filter_presets import (
    load_presets, add_preset, delete_preset, get_preset, get_all_preset_names
)
from app.modules.devicevault.exporter import (
    export_devices_csv, 
    export_devices_json, 
    export_full_inventory_json
)
from app.modules.devicevault.reporter import (
    generate_markdown_report,
    generate_html_report
)
from app.core.logger import logger
from app.gui.theme import Theme

class DeviceVaultPage(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(18)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("DeviceVault")
        title.setStyleSheet(Theme.page_title_style())
        subtitle = QLabel("Persistent local network asset inventory")
        subtitle.setStyleSheet(Theme.page_subtitle_style())
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        main_layout.addLayout(header_layout)
        
        notice_label = QLabel("ℹ️ Device inventory is stored locally on this machine.")
        notice_label.setStyleSheet(Theme.notice_style("info"))
        main_layout.addWidget(notice_label)

        # Inventory Hygiene Insights with Quick Filters (Phase 8I - compact buttons, safe filters, no redesign)
        hygiene_frame = QFrame()
        hygiene_frame.setStyleSheet(Theme.section_frame_style())
        hygiene_layout = QHBoxLayout(hygiene_frame)
        hygiene_layout.setContentsMargins(12, 8, 12, 8)
        hygiene_layout.setSpacing(6)
        
        self.hygiene_labels = {}
        self.active_hygiene_filter = None
        items = [
            ("Unclassified", "unclassified"),
            ("Missing Name", "missing_name"),
            ("Missing Vendor", "missing_vendor"),
            ("TLS Warnings", "tls_warnings"),
            ("Stale (>7d)", "stale")
        ]
        for text, key in items:
            lbl = QLabel(f"{text}: 0")
            lbl.setStyleSheet(Theme.hygiene_badge_style())
            hygiene_layout.addWidget(lbl)
            self.hygiene_labels[key] = lbl
            
            btn = QPushButton("Show")
            btn.setStyleSheet(Theme.hygiene_btn_style())
            btn.clicked.connect(lambda _, k=key: self.apply_hygiene_filter(k))
            hygiene_layout.addWidget(btn)
        
        self.btn_clear_hygiene = QPushButton("Clear Filters")
        self.btn_clear_hygiene.setStyleSheet(Theme.danger_btn_style())
        self.btn_clear_hygiene.clicked.connect(self.clear_all_filters)
        hygiene_layout.addWidget(self.btn_clear_hygiene)
        hygiene_layout.addStretch()
        main_layout.addWidget(hygiene_frame)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by IP, Name, MAC, Vendor, Tags...")
        self.search_input.setStyleSheet(Theme.input_style())
        self.search_input.textChanged.connect(self.load_devices)
        search_layout.addWidget(self.search_input)
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_refresh.setStyleSheet(Theme.primary_btn_style())
        self.btn_refresh.clicked.connect(self.load_devices)
        search_layout.addWidget(self.btn_refresh)
        
        main_layout.addLayout(search_layout)

        # Bulk Classification Controls (Phase 8F - compact, near controls, no redesign)
        bulk_layout = QHBoxLayout()
        bulk_label = QLabel("Bulk:")
        bulk_label.setStyleSheet(Theme.muted_label_style())
        bulk_layout.addWidget(bulk_label)

        self.bulk_type_combo = QComboBox()
        self.bulk_type_combo.addItems([
            "Router", "Server", "Workstation", "Laptop", "NAS", "VM", 
            "IoT", "Phone", "Printer", "Unclassified"
        ])
        self.bulk_type_combo.setMinimumWidth(120)
        self.bulk_type_combo.setStyleSheet(Theme.combo_style())
        bulk_layout.addWidget(self.bulk_type_combo)

        self.btn_apply_bulk_type = QPushButton("Apply Type to Selected")
        self.btn_apply_bulk_type.setStyleSheet(Theme.secondary_btn_style())
        self.btn_apply_bulk_type.clicked.connect(self.apply_bulk_type)
        bulk_layout.addWidget(self.btn_apply_bulk_type)

        self.bulk_tag_input = QLineEdit()
        self.bulk_tag_input.setPlaceholderText("Add tag to selected devices")
        self.bulk_tag_input.setMinimumWidth(150)
        self.bulk_tag_input.setStyleSheet(Theme.input_style())
        bulk_layout.addWidget(self.bulk_tag_input)

        self.btn_add_bulk_tag = QPushButton("Add Tag to Selected")
        self.btn_add_bulk_tag.setStyleSheet(Theme.secondary_btn_style())
        self.btn_add_bulk_tag.clicked.connect(self.add_bulk_tag)
        bulk_layout.addWidget(self.btn_add_bulk_tag)

        bulk_layout.addStretch()
        main_layout.addLayout(bulk_layout)

        # Export buttons (minimal addition)
        export_layout = QHBoxLayout()
        export_label = QLabel("Export:")
        self.scope_combo = QComboBox()
        self.scope_combo.addItems(["Full Inventory", "Current Filtered View", "Selected Devices"])
        self.scope_combo.setCurrentText("Full Inventory")
        self.scope_combo.setMinimumWidth(160)
        self.scope_combo.setStyleSheet(Theme.combo_style())
        export_layout.addWidget(self.scope_combo)
        export_layout.addWidget(export_label)
        export_label.setStyleSheet(Theme.muted_label_style())
        export_layout.addWidget(export_label)
        
        self.btn_export_csv = QPushButton("Devices CSV")
        self.btn_export_csv.setStyleSheet(Theme.secondary_btn_style())
        self.btn_export_csv.clicked.connect(self.export_devices_to_csv)
        export_layout.addWidget(self.btn_export_csv)
        
        self.btn_export_json = QPushButton("Devices JSON")
        self.btn_export_json.setStyleSheet(Theme.secondary_btn_style())
        self.btn_export_json.clicked.connect(self.export_devices_to_json)
        export_layout.addWidget(self.btn_export_json)
        
        self.btn_export_full = QPushButton("Full Inventory JSON")
        self.btn_export_full.setStyleSheet(Theme.secondary_btn_style())
        self.btn_export_full.clicked.connect(self.export_full_inventory)
        export_layout.addWidget(self.btn_export_full)
        
        # Minimal report buttons (Phase 7C)
        self.btn_report_md = QPushButton("Generate Markdown Report")
        self.btn_report_md.setStyleSheet(Theme.secondary_btn_style())
        self.btn_report_md.clicked.connect(self.generate_markdown_report)
        export_layout.addWidget(self.btn_report_md)
        
        self.btn_report_html = QPushButton("Generate HTML Report")
        self.btn_report_html.setStyleSheet(Theme.secondary_btn_style())
        self.btn_report_html.clicked.connect(self.generate_html_report)
        export_layout.addWidget(self.btn_report_html)
        
        export_layout.addStretch()
        main_layout.addLayout(export_layout)
        
        # Content Splitter (Table + Edit Details)
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        
        # Table Container
        self.table_container = QWidget()
        self.table_layout = QVBoxLayout(self.table_container)
        self.table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_empty_state = QLabel("No devices saved yet. Run an IPHawk scan and save results to DeviceVault.")
        self.lbl_empty_state.setAlignment(Qt.AlignCenter)
        self.lbl_empty_state.setStyleSheet(Theme.empty_state_style())
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
        
        self.table.setStyleSheet(Theme.table_style())
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        self.table_layout.addWidget(self.table)
        splitter.addWidget(self.table_container)
        
        # Details Panel Container
        self.details_panel_container = QFrame()
        # Override padding so scrollbar is flush with border
        self.details_panel_container.setStyleSheet(Theme.details_panel_style() + "QFrame { padding: 0px; }")
        self.details_panel_container.setMinimumWidth(350)
        
        container_layout = QVBoxLayout(self.details_panel_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.details_panel = QWidget()
        self.details_panel.setStyleSheet("background: transparent;")
        self.details_layout = QVBoxLayout(self.details_panel)
        self.details_layout.setAlignment(Qt.AlignTop)
        self.details_layout.setContentsMargins(20, 20, 20, 20)
        self.details_layout.setSpacing(10)
        
        self.details_scroll.setWidget(self.details_panel)
        container_layout.addWidget(self.details_scroll)
        
        panel_title = QLabel("Device Details & Edit")
        panel_title.setStyleSheet(Theme.panel_title_style())
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
            lbl.setStyleSheet(Theme.detail_label_style())
            lbl.setWordWrap(True)
            self.details_layout.addWidget(lbl)
            
        self.details_layout.addSpacing(10)
        
        # Editable fields
        self.lbl_name_edit = QLabel("Custom Name:")
        self.lbl_name_edit.setStyleSheet(Theme.field_label_style())
        self.details_layout.addWidget(self.lbl_name_edit)
        self.edit_name = QLineEdit()
        self.edit_name.setStyleSheet(Theme.inline_edit_style())
        self.details_layout.addWidget(self.edit_name)
        
        self.lbl_type_edit = QLabel("Device Type:")
        self.lbl_type_edit.setStyleSheet(Theme.field_label_style())
        self.details_layout.addWidget(self.lbl_type_edit)
        self.edit_type = QComboBox()
        self.edit_type.addItems([
            "Unclassified", "Router", "Switch", "Firewall", "NAS", "Server", "Workstation", 
            "Laptop", "Virtual Machine", "Container", "IoT Device", "Printer", "Mobile Device", "Other"
        ])
        self.edit_type.setStyleSheet(Theme.inline_edit_style())
        self.details_layout.addWidget(self.edit_type)
        
        self.lbl_tags_edit = QLabel("Tags (comma separated):")
        self.lbl_tags_edit.setStyleSheet(Theme.field_label_style())
        self.details_layout.addWidget(self.lbl_tags_edit)
        self.edit_tags = QLineEdit()
        self.edit_tags.setStyleSheet(Theme.inline_edit_style())
        self.details_layout.addWidget(self.edit_tags)
        
        self.lbl_notes_edit = QLabel("Notes:")
        self.lbl_notes_edit.setStyleSheet(Theme.field_label_style())
        self.details_layout.addWidget(self.lbl_notes_edit)
        self.edit_notes = QTextEdit()
        self.edit_notes.setMaximumHeight(80)
        self.details_layout.addWidget(self.edit_notes)
        
        self.btn_save_changes = QPushButton("Save Changes")
        self.btn_save_changes.setStyleSheet(Theme.success_btn_style())
        self.btn_save_changes.clicked.connect(self.save_manual_edits)
        self.btn_save_changes.setEnabled(False)
        self.details_layout.addWidget(self.btn_save_changes)
        
        self.details_layout.addSpacing(15)
        
        # Open Services Section
        services_title = QLabel("OPEN SERVICES")
        services_title.setStyleSheet(Theme.section_title_style())
        self.details_layout.addWidget(services_title)
        
        self.lbl_no_services = QLabel("No services saved yet.")
        self.lbl_no_services.setStyleSheet(Theme.no_data_label_style())
        self.details_layout.addWidget(self.lbl_no_services)
        
        self.services_table = QTableWidget(0, 5)
        self.services_table.setHorizontalHeaderLabels(["Port", "Protocol", "Service", "State", "Last Seen"])
        self.services_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.services_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.services_table.setStyleSheet(Theme.compact_table_style())
        self.services_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.services_table.setSelectionMode(QTableWidget.NoSelection)
        self.services_table.setAlternatingRowColors(True)
        self.services_table.verticalHeader().setVisible(False)
        self.services_table.setMaximumHeight(150)
        self.services_table.hide()
        self.details_layout.addWidget(self.services_table)
        
        # Web Metadata Section
        web_title = QLabel("WEB METADATA")
        web_title.setStyleSheet(Theme.section_title_style())
        self.details_layout.addWidget(web_title)
        
        self.lbl_no_web = QLabel("No web metadata saved yet. Run WebPulse and save results.")
        self.lbl_no_web.setStyleSheet(Theme.no_data_label_style())
        self.details_layout.addWidget(self.lbl_no_web)
        
        self.web_table = QTableWidget(0, 7)
        self.web_table.setHorizontalHeaderLabels(["URL", "Status", "HTTP Code", "Title", "Server", "SSL Expiry", "Last Checked"])
        self.web_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.web_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.web_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.web_table.setStyleSheet(Theme.compact_table_style())
        self.web_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.web_table.setSelectionMode(QTableWidget.NoSelection)
        self.web_table.setAlternatingRowColors(True)
        self.web_table.verticalHeader().setVisible(False)
        self.web_table.setMaximumHeight(150)
        self.web_table.hide()
        self.details_layout.addWidget(self.web_table)
        
        splitter.addWidget(self.details_panel_container)
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
            hygiene = getattr(self, 'active_hygiene_filter', None)
            if query or hygiene:
                devices = DeviceVaultService.get_filtered_devices(
                    db, query, "All", "All", "All", hygiene
                )
            else:
                devices = DeviceVaultService.get_all_devices(db)
            
            self.table.setRowCount(0)
            
            if not devices and not query:
                self.table.hide()
                self.lbl_empty_state.show()
                self.details_panel_container.hide()
            else:
                self.table.show()
                self.lbl_empty_state.hide()
                self.details_panel_container.show()
                
            for d in devices:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                self.table.setItem(row, 0, QTableWidgetItem(str(d.id)))
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
            self.update_hygiene_summary()

    def apply_hygiene_filter(self, filter_type):
        """Set active hygiene filter and reload with get_filtered_devices."""
        self.active_hygiene_filter = filter_type
        self.load_devices()
        if hasattr(self, 'filter_summary_label') and self.filter_summary_label:
            self.filter_summary_label.setText(f"Filters: Hygiene = {filter_type.replace('_', ' ').title()}")
        if hasattr(self, 'update_hygiene_summary'):
            self.update_hygiene_summary()

    def clear_all_filters(self):
        """Clear hygiene filter and search. Safe for current implementation."""
        self.active_hygiene_filter = None
        self.search_input.clear()
        if hasattr(self, 'filter_summary_label') and self.filter_summary_label:
            self.filter_summary_label.setText("No active filters")
        self.load_devices()
        if hasattr(self, 'update_hygiene_summary'):
            self.update_hygiene_summary()

    def get_selected_device_ids(self):
        """Get list of device IDs from currently selected table rows (supports multi-select)."""
        ids = []
        selected_rows = set()
        for item in self.table.selectedItems():
            row = item.row()
            if row not in selected_rows:
                selected_rows.add(row)
                id_item = self.table.item(row, 0)
                if id_item:
                    try:
                        ids.append(int(id_item.text()))
                    except ValueError:
                        pass
        return list(set(ids))

    def apply_bulk_type(self):
        """Apply selected device type to all currently selected devices."""
        device_ids = self.get_selected_device_ids()
        if not device_ids:
            QMessageBox.information(self, "No Selection", "No devices selected.")
            return
        device_type = self.bulk_type_combo.currentText()
        reply = QMessageBox.question(self, "Confirm Bulk Update", f"Update device type to '{device_type}' for {len(device_ids)} selected devices?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        db = SessionLocal()
        try:
            updated = DeviceVaultService.bulk_update_device_type(db, device_ids, device_type)
            QMessageBox.information(self, "Success", f"Updated {updated} selected devices.")
            self.load_devices()
        finally:
            db.close()

    def add_bulk_tag(self):
        """Add tag to all currently selected devices."""
        device_ids = self.get_selected_device_ids()
        if not device_ids:
            QMessageBox.information(self, "No Selection", "No devices selected.")
            return
        tag = self.bulk_tag_input.text().strip()
        if not tag:
            QMessageBox.information(self, "No Tag", "Enter a tag first.")
            return
        reply = QMessageBox.question(self, "Confirm Bulk Tag", f"Add tag '{tag}' to {len(device_ids)} selected devices?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        db = SessionLocal()
        try:
            updated = DeviceVaultService.bulk_add_tag(db, device_ids, tag)
            QMessageBox.information(self, "Success", f"Added tag to {updated} selected devices.")
            self.bulk_tag_input.clear()
            self.load_devices()
        finally:
            db.close()


    def export_devices_to_csv(self):
        scope = getattr(self, 'scope_combo', None)
        scope_text = scope.currentText() if scope else "Full Inventory"
        device_ids = self.get_selected_device_ids() if scope_text == "Selected Devices" else None
        if scope_text == "Selected Devices" and not device_ids:
            QMessageBox.information(self, "No Selection", "No devices selected.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Devices CSV", "devices.csv", "CSV Files (*.csv);;All Files (*)")
        if not path:
            return
        if not path.endswith(".csv"):
            path += ".csv"
        if export_devices_csv(path, device_ids=device_ids):
            self._show_export_success(path)
        else:
            self._show_no_data()

    def export_devices_to_json(self):
        scope = getattr(self, 'scope_combo', None)
        scope_text = scope.currentText() if scope else "Full Inventory"
        device_ids = self.get_selected_device_ids() if scope_text == "Selected Devices" else None
        if scope_text == "Selected Devices" and not device_ids:
            QMessageBox.information(self, "No Selection", "No devices selected.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export Devices JSON", "devices.json", "JSON Files (*.json);;All Files (*)")
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"
        if export_devices_json(path, device_ids=device_ids):
            self._show_export_success(path)
        else:
            self._show_no_data()

    def export_full_inventory(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Full Inventory JSON", "inventory.json", "JSON Files (*.json);;All Files (*)")
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"
        if export_full_inventory_json(path):
            self._show_export_success(path)
        else:
            self._show_no_data()

    def generate_markdown_report(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Markdown Report", "inventory-report.md", "Markdown Files (*.md);;All Files (*)")
        if not path:
            return
        if not path.endswith(".md"):
            path += ".md"
        scope = getattr(self, 'scope_combo', None)
        scope_text = scope.currentText() if scope else "Full Inventory"
        device_ids = self.get_selected_device_ids() if scope_text == "Selected Devices" else None
        if scope_text == "Selected Devices" and not device_ids:
            QMessageBox.information(self, "No Selection", "No devices selected.")
            return
        if generate_markdown_report(path, device_ids=device_ids, scope_label=scope_text):
            QMessageBox.information(self, "Success", f"Markdown report saved to:\n{path}")
        else:
            self._show_no_data()

    def generate_html_report(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save HTML Report", "inventory-report.html", "HTML Files (*.html);;All Files (*)")
        if not path:
            return
        if not path.endswith(".html"):
            path += ".html"
        scope = getattr(self, 'scope_combo', None)
        scope_text = scope.currentText() if scope else "Full Inventory"
        device_ids = self.get_selected_device_ids() if scope_text == "Selected Devices" else None
        if scope_text == "Selected Devices" and not device_ids:
            QMessageBox.information(self, "No Selection", "No devices selected.")
            return
        if generate_html_report(path, device_ids=device_ids, scope_label=scope_text):
            QMessageBox.information(self, "Success", f"HTML report saved to:\n{path}")
        else:
            self._show_no_data()

    def _show_export_success(self, path: str):
        QMessageBox.information(self, "Export Successful", f"Data exported to:\n{path}")

    def _show_no_data(self):
        QMessageBox.information(self, "No Data", "No data available to export.")




    def update_hygiene_summary(self):
        db = SessionLocal()
        try:
            summary = DeviceVaultService.get_inventory_hygiene_summary(db)
            for key, count in summary.items():
                if key in getattr(self, 'hygiene_labels', {}):
                    text = key.replace('_', ' ').title()
                    self.hygiene_labels[key].setText(f"{text}: {count}")
        except Exception as e:
            logger.error(f"Hygiene update error: {e}")
        finally:
            db.close()

    @Slot()
    def on_selection_changed(self):
        selected = self.table.selectedItems()
        if not selected:
            self.current_device_id = None
            if hasattr(self, 'btn_save_changes'):
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
        
        extra_data = self.table.item(row, 0).data(Qt.UserRole) or {}
        
        if hasattr(self, 'lbl_ip'):
            self.lbl_ip.setText(f"<b>IP Address:</b> {ip}")
        if hasattr(self, 'lbl_mac'):
            self.lbl_mac.setText(f"<b>MAC Address:</b> {mac}")
        if hasattr(self, 'lbl_vendor'):
            self.lbl_vendor.setText(f"<b>Vendor:</b> {vendor}")
        if hasattr(self, 'lbl_detected_host'):
            self.lbl_detected_host.setText(f"<b>Detected Hostname:</b> {extra_data.get('detected_hostname', '—')}")
        if hasattr(self, 'lbl_source'):
            self.lbl_source.setText(f"<b>Discovery Source:</b> {extra_data.get('discovery_source', '—')}")
        if hasattr(self, 'lbl_confidence'):
            self.lbl_confidence.setText(f"<b>Confidence:</b> {extra_data.get('confidence', '—')}")
        if hasattr(self, 'lbl_first_seen'):
            self.lbl_first_seen.setText(f"<b>First Seen:</b> {extra_data.get('first_seen', '—')}")
        if hasattr(self, 'lbl_last_seen'):
            self.lbl_last_seen.setText(f"<b>Last Seen:</b> {last_seen}")
        
        if hasattr(self, 'edit_name'):
            self.edit_name.setText(name if name != "—" else "")
        if hasattr(self, 'edit_type'):
            index = self.edit_type.findText(dev_type)
            if index >= 0: 
                self.edit_type.setCurrentIndex(index)
            else: 
                self.edit_type.setCurrentIndex(0)
        if hasattr(self, 'edit_tags') and 'tags' in extra_data:
            self.edit_tags.setText(extra_data['tags'])
        if hasattr(self, 'edit_notes') and 'notes' in extra_data:
            self.edit_notes.setPlainText(extra_data['notes'])
        
        if hasattr(self, 'btn_save_changes'):
            self.btn_save_changes.setEnabled(True)
        
        # Load services and web (simplified)
        db = SessionLocal()
        try:
            if hasattr(self, 'services_table') and hasattr(self, 'lbl_no_services'):
                services = DeviceVaultService.get_device_services(db, self.current_device_id)
                if services and hasattr(self, 'services_table'):
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
                    if hasattr(self, 'services_table'):
                        self.services_table.hide()
                    if hasattr(self, 'lbl_no_services'):
                        self.lbl_no_services.show()
        finally:
            db.close()

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
