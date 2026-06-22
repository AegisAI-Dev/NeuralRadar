from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGridLayout
)
from PySide6.QtCore import Qt, Slot
from app.modules.devicevault.service import DeviceVaultService
from app.core.database import SessionLocal
from app.core.logger import logger
from app.core.version import VERSION


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # Header
        header = QLabel("Dashboard Intelligence Overview")
        header.setStyleSheet("color: #cdd6f4; font-size: 28px; font-weight: bold;")
        main_layout.addWidget(header)
        
        notice = QLabel("All data is local-only. No network checks or scans performed by dashboard.")
        notice.setStyleSheet("color: #a6e3a1; font-size: 13px; background-color: #313244; padding: 10px; border-radius: 6px;")
        main_layout.addWidget(notice)
        
        # Intelligence Overview
        overview_frame = QFrame()
        overview_frame.setStyleSheet("background-color: #1e1e2e; border: 1px solid #313244; border-radius: 6px; padding: 15px;")
        overview_layout = QGridLayout(overview_frame)
        overview_layout.setSpacing(15)
        
        self.summary_labels = {}
        self.summary_keys = [
            'total_devices', 'unclassified_devices', 'missing_names', 'missing_vendors',
            'stored_open_services', 'stored_web_endpoints', 'tls_warnings',
            'expired_tls_count', 'expiring_tls_count', 'last_inventory_update'
        ]
        labels_text = [
            "Total Devices", "Needing Classification", "Missing Name", "Missing Vendor",
            "Stored Open Services", "Stored Web Endpoints", "TLS Warnings",
            "Expired TLS", "Expiring TLS (30d)", "Last Inventory Update"
        ]
        
        for i, (key, text) in enumerate(zip(self.summary_keys, labels_text)):
            card = QFrame()
            card.setStyleSheet("background-color: #313244; border-radius: 6px; padding: 15px;")
            card_layout = QVBoxLayout(card)
            title = QLabel(text)
            title.setStyleSheet("color: #89b4fa; font-size: 13px; font-weight: bold;")
            value = QLabel("0")
            value.setStyleSheet("color: #cdd6f4; font-size: 24px; font-weight: bold;")
            card_layout.addWidget(title)
            card_layout.addWidget(value)
            overview_layout.addWidget(card, i // 3, i % 3)
            self.summary_labels[key] = value
        
        main_layout.addWidget(overview_frame)
        
        # Attention Needed
        attention_frame = QFrame()
        attention_frame.setStyleSheet("background-color: #1e1e2e; border: 1px solid #313244; border-radius: 6px; padding: 15px;")
        attention_layout = QVBoxLayout(attention_frame)
        
        attention_title = QLabel("Attention Needed")
        attention_title.setStyleSheet("color: #f38ba8; font-size: 16px; font-weight: bold;")
        attention_layout.addWidget(attention_title)
        
        self.attention_label = QLabel("Loading local intelligence...")
        self.attention_label.setStyleSheet("color: #a6adc8; font-size: 13px;")
        attention_layout.addWidget(self.attention_label)
        
        main_layout.addWidget(attention_frame)
        
        # Quick Actions
        actions_frame = QFrame()
        actions_frame.setStyleSheet("background-color: #1e1e2e; border: 1px solid #313244; border-radius: 6px; padding: 15px;")
        actions_layout = QHBoxLayout(actions_frame)
        
        actions_title = QLabel("Quick Actions")
        actions_title.setStyleSheet("color: #cdd6f4; font-size: 16px; font-weight: bold;")
        actions_layout.addWidget(actions_title)
        
        for page in ["DeviceVault", "IPHawk", "PortScope", "WebPulse"]:
            btn = QPushButton(f"Open {page}")
            btn.setStyleSheet("background-color: #313244; color: #89b4fa; padding: 8px 15px; border-radius: 4px;")
            # In full integration, this would emit a signal for main_window to switch tabs.
            # For this phase, guidance text only to avoid editing other GUI files.
            btn.clicked.connect(lambda _, p=page: logger.info(f"Guidance: Open {p} from main navigation."))
            actions_layout.addWidget(btn)
        
        main_layout.addWidget(actions_frame)
        
        self.refresh_dashboard()
        
    def refresh_dashboard(self):
        """Refresh intelligence using local data only. No scans or network calls."""
        db = SessionLocal()
        try:
            summary = DeviceVaultService.get_dashboard_intelligence_summary(db)
            for key in self.summary_labels:
                if key in summary:
                    value = summary[key]
                    if key in ['expired_tls_count', 'expiring_tls_count']:
                        self.summary_labels[key].setText(str(value))
                    else:
                        self.summary_labels[key].setText(str(value))
            
            attention_items = []
            if summary['unclassified_devices'] > 0:
                attention_items.append(f"{summary['unclassified_devices']} devices are unclassified")
            if summary['missing_names'] > 0:
                attention_items.append(f"{summary['missing_names']} devices are missing name information")
            if summary['missing_vendors'] > 0:
                attention_items.append(f"{summary['missing_vendors']} devices are missing vendor information")
            if summary['tls_warnings'] > 0:
                attention_items.append(f"{summary['tls_warnings']} web endpoints have TLS warnings")
            if summary['expired_tls_count'] > 0:
                attention_items.append(f"{summary['expired_tls_count']} TLS certificates are expired")
            if summary['expiring_tls_count'] > 0:
                attention_items.append(f"{summary['expiring_tls_count']} TLS certificates expiring soon")
            
            if attention_items:
                self.attention_label.setText("\n".join(attention_items))
                self.attention_label.setStyleSheet("color: #f38ba8; font-size: 13px;")
            else:
                self.attention_label.setText("No attention items found. Local inventory is well-maintained.")
                self.attention_label.setStyleSheet("color: #a6e3a1; font-size: 13px;")
        except Exception as e:
            logger.error(f"Dashboard refresh error: {e}")
            self.attention_label.setText("Error loading local intelligence.")
        finally:
            db.close()
    
    @Slot()
    def on_refresh_clicked(self):
        """Called by existing Refresh Stats button if wired in main_window."""
        self.refresh_dashboard()

    def update_device_relationships(self):
        """Update Device Relationship Overview from local stored data only. No scans or network calls."""
        db = SessionLocal()
        try:
            relationships = DeviceVaultService.get_device_relationship_summary(db, limit=8)
            # Clear previous items
            while self.relationship_layout.count():
                item = self.relationship_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            
            if not relationships:
                self.relationship_empty_label.show()
                return
            
            self.relationship_empty_label.hide()
            for rel in relationships:
                item_text = f"{rel['name']}\nServices: {rel['service_count']} | Web endpoints: {rel['web_endpoint_count']} | TLS attention: {rel['tls_attention_count']} | Last seen: {rel['last_seen']}"
                item_label = QLabel(item_text)
                item_label.setStyleSheet("color: #a6adc8; font-size: 13px; background-color: #313244; padding: 8px; border-radius: 4px;")
                item_label.setWordWrap(True)
                self.relationship_layout.addWidget(item_label)
        except Exception as e:
            logger.error(f"Device relationship update error: {e}")
            error_label = QLabel("Error loading local relationships.")
            error_label.setStyleSheet("color: #f38ba8; font-size: 13px;")
            self.relationship_layout.addWidget(error_label)
        finally:
            db.close()
