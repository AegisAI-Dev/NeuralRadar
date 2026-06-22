from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea, QGridLayout, QSplitter
)
from PySide6.QtCore import Qt, Slot
from app.modules.devicevault.service import DeviceVaultService
from app.core.database import SessionLocal
from app.core.logger import logger
from app.gui.theme import Theme


class NetMapPage(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header Area
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        
        header = QLabel("NetMap")
        header.setStyleSheet(Theme.page_title_style())
        title_layout.addWidget(header)
        
        subtitle = QLabel("Local relationship map from stored DeviceVault data")
        subtitle.setStyleSheet(Theme.page_subtitle_style())
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Refresh Button moved to top right
        self.btn_refresh_netmap = QPushButton("Refresh")
        self.btn_refresh_netmap.setStyleSheet(Theme.secondary_btn_style())
        self.btn_refresh_netmap.clicked.connect(self.refresh_netmap)
        header_layout.addWidget(self.btn_refresh_netmap)
        
        main_layout.addLayout(header_layout)
        
        safety_banner = QLabel("Local-only view. No scans are triggered from this page.")
        safety_banner.setStyleSheet(Theme.notice_style("info"))
        main_layout.addWidget(safety_banner)
        
        # Summary Cards
        summary_frame = QFrame()
        summary_frame.setStyleSheet("background: transparent; border: none;")
        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(0, 0, 0, 0)
        summary_layout.setSpacing(15)
        
        self.summary_cards = {}
        card_data = [
            ("Devices", "total_devices"),
            ("Stored Services", "stored_open_services"),
            ("Web Endpoints", "stored_web_endpoints"),
            ("TLS Attention", "tls_warnings")
        ]
        for title, key in card_data:
            card = QFrame()
            card.setStyleSheet(Theme.get_card_style(is_active=False))
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(20, 15, 20, 15)
            
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet(f"color: {Theme.COLORS.PRIMARY_DIM}; font-size: 12px; font-weight: 600; text-transform: uppercase; border: none;")
            
            value_lbl = QLabel("0")
            value_lbl.setStyleSheet(f"color: {Theme.COLORS.TEXT_BRIGHT}; font-size: 28px; font-weight: bold; border: none;")
            
            card_layout.addWidget(title_lbl)
            card_layout.addWidget(value_lbl)
            summary_layout.addWidget(card)
            self.summary_cards[key] = value_lbl
        
        main_layout.addWidget(summary_frame)
        
        # Relationship List
        self.relationship_scroll = QScrollArea()
        self.relationship_scroll.setWidgetResizable(True)
        self.relationship_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget#scroll_content { background: transparent; }")
        
        self.relationship_content = QWidget()
        self.relationship_content.setObjectName("scroll_content")
        self.relationship_layout = QVBoxLayout(self.relationship_content)
        self.relationship_layout.setSpacing(10)
        self.relationship_layout.setContentsMargins(0, 0, 10, 0)
        self.relationship_layout.setAlignment(Qt.AlignTop)
        self.relationship_scroll.setWidget(self.relationship_content)

        # Detail panel
        self.detail_splitter = QSplitter(Qt.Horizontal)
        self.detail_splitter.addWidget(self.relationship_scroll)

        self.detail_frame = QFrame()
        self.detail_frame.setStyleSheet(Theme.details_panel_style())
        self.detail_layout = QVBoxLayout(self.detail_frame)
        self.detail_layout.setAlignment(Qt.AlignTop)

        self.detail_title = QLabel("Device Details")
        self.detail_title.setStyleSheet(Theme.panel_title_style())
        self.detail_layout.addWidget(self.detail_title)

        self.detail_content = QLabel("Select a device to see stored relationships.")
        self.detail_content.setStyleSheet(Theme.detail_label_style())
        self.detail_content.setWordWrap(True)
        self.detail_content.setAlignment(Qt.AlignTop)
        self.detail_layout.addWidget(self.detail_content)

        self.detail_splitter.addWidget(self.detail_frame)
        self.detail_splitter.setStretchFactor(0, 5)
        self.detail_splitter.setStretchFactor(1, 3)
        main_layout.addWidget(self.detail_splitter)


        self.refresh_netmap()
        
    def refresh_netmap(self):
        """Refresh NetMap from local stored data only. No scans or network calls."""
        db = SessionLocal()
        try:
            data = DeviceVaultService.get_device_relationship_summary(db, limit=50)
            
            # Update summary cards
            total_devices = len(data)
            stored_services = sum(d.get('service_count', 0) for d in data)
            stored_web = sum(d.get('web_endpoint_count', 0) for d in data)
            tls_attention = sum(d.get('tls_attention_count', 0) for d in data)
            
            if 'total_devices' in self.summary_cards:
                self.summary_cards['total_devices'].setText(str(total_devices))
            if 'stored_open_services' in self.summary_cards:
                self.summary_cards['stored_open_services'].setText(str(stored_services))
            if 'stored_web_endpoints' in self.summary_cards:
                self.summary_cards['stored_web_endpoints'].setText(str(stored_web))
            if 'tls_warnings' in self.summary_cards:
                self.summary_cards['tls_warnings'].setText(str(tls_attention))
            
            # Clear previous relationships
            while self.relationship_layout.count():
                item = self.relationship_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            if not data:
                empty_label = QLabel("No local relationship data yet.\nRun IPHawk, save devices to DeviceVault, then optionally use PortScope and WebPulse to enrich services and endpoints.")
                empty_label.setStyleSheet(Theme.empty_state_style())
                empty_label.setAlignment(Qt.AlignCenter)
                self.relationship_layout.addWidget(empty_label)
                return
            
            for rel in data:
                card = QFrame()
                card.setStyleSheet(Theme.get_card_style(is_active=False))
                card.setCursor(Qt.PointingHandCursor)
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                
                title = QLabel(f"{rel['name']} ({rel['ip_address']})")
                title.setStyleSheet(f"color: {Theme.COLORS.TEXT_BRIGHT}; font-size: 14px; font-weight: bold; border: none;")
                card_layout.addWidget(title)
                
                details = QLabel(f"Services: {rel.get('service_count', 0)} | Web endpoints: {rel.get('web_endpoint_count', 0)} | TLS attention: {rel.get('tls_attention_count', 0)} | Last seen: {rel.get('last_seen', '—')}")
                details.setStyleSheet(f"color: {Theme.COLORS.MUTED}; font-size: 13px; border: none;")
                details.setWordWrap(True)
                card_layout.addWidget(details)
                
                self.relationship_layout.addWidget(card)
                card.mousePressEvent = lambda event, d=rel: self.show_device_details(d)

        except Exception as e:
            logger.error(f"NetMap refresh error: {e}")
            error_label = QLabel("Error loading local relationship data.")
            error_label.setStyleSheet(Theme.notice_style("danger"))
            self.relationship_layout.addWidget(error_label)
        finally:
            db.close()
    
    @Slot()
    def on_refresh_clicked(self):
        """Called by existing Refresh Stats if wired, or NetMap Refresh button."""
        self.refresh_netmap()

    def show_device_details(self, device):
        """Show local device detail drilldown (stored data only, no scan)."""
        db = SessionLocal()
        try:
            details = DeviceVaultService.get_device_relationship_details(db, device['device_id'])
            if not details:
                self.detail_content.setText("Device not found in local inventory.")
                return
            html = f"<b>{details['name']}</b> ({details['ip_address']})<br>"
            html += f"Type: {details['device_type']}<br>"
            html += f"Vendor: {details['vendor']}<br>"
            html += f"Status: {details['status']}<br>"
            html += f"Last seen: {details['last_seen']}<br><br>"
            html += f"<b>Stored Services ({len(details['services'])})</b><br>"
            if details['services']:
                for s in details['services']:
                    html += f"• {s['port']}/{s['protocol']} - {s['service']} ({s['state']})<br>"
            else:
                html += "No stored services.<br>"
            html += "<br><b>Stored Web Endpoints ({len(details['web_endpoints'])})</b><br>"
            if details['web_endpoints']:
                for w in details['web_endpoints']:
                    html += f"• {w['url']} ({w['status']}) - {w['server']}<br>"
            else:
                html += "No stored web endpoints.<br>"
            self.detail_content.setText(html)
        except Exception as e:
            logger.error(f"Device detail error: {e}")
            self.detail_content.setText("Error loading local device details.")
        finally:
            db.close()
