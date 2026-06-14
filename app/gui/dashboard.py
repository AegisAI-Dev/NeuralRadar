from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt

class ModuleCard(QFrame):
    def __init__(self, title, description):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            ModuleCard {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 8px;
            }
            ModuleCard:hover {
                border: 1px solid #89b4fa;
            }
        """)
        self.setFixedSize(250, 150)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #cdd6f4; font-size: 16px; font-weight: bold; border: none; background: transparent;")
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("color: #a6adc8; font-size: 12px; border: none; background: transparent;")
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        self.setLayout(layout)

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)
        
        # Header
        header_layout = QVBoxLayout()
        title = QLabel("NeuralRadar Dashboard")
        title.setStyleSheet("color: #cdd6f4; font-size: 28px; font-weight: bold;")
        subtitle = QLabel("Network discovery, mapping and monitoring platform by NeuralShield")
        subtitle.setStyleSheet("color: #89b4fa; font-size: 14px;")
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        
        main_layout.addLayout(header_layout)
        
        # Scroll Area for Cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e2e;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #313244;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #45475a;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        grid_layout = QGridLayout(scroll_content)
        grid_layout.setSpacing(20)
        grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        modules = [
            ("IPHawk", "IP discovery and active host detection module. (Coming soon)"),
            ("PortScope", "Comprehensive port scanning and service identification. (Coming soon)"),
            ("DeviceVault", "Persistent device inventory and asset management. (Coming soon)"),
            ("NetMap", "Visual, interactive network topology mapping. (Coming soon)"),
            ("WatchTower", "Uptime and latency monitoring for critical network assets. (Coming soon)"),
            ("WebPulse", "Website, API, and SSL certificate health checks. (Coming soon)"),
            ("ShieldAudit", "Basic security checks and vulnerability scanning. (Coming soon)"),
            ("ContainerRadar", "Overview of Docker, LXC, and Proxmox environments. (Coming soon)")
        ]
        
        row, col = 0, 0
        for title, desc in modules:
            card = ModuleCard(title, desc)
            grid_layout.addWidget(card, row, col)
            col += 1
            if col > 3:  # 4 columns max
                col = 0
                row += 1
                
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
