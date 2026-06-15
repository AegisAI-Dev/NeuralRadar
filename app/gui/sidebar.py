from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setStyleSheet("""
            Sidebar {
                background-color: #11111b;
                border-right: 1px solid #313244;
            }
            QPushButton {
                background-color: transparent;
                color: #a6adc8;
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                margin: 2px 10px;
            }
            QPushButton:hover {
                background-color: #313244;
                color: #cdd6f4;
            }
            QPushButton:checked {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 30, 0, 20)
        layout.setSpacing(5)
        
        # Logo placeholder
        logo_label = QLabel("NeuralRadar")
        logo_label.setStyleSheet("color: #89b4fa; font-size: 24px; font-weight: bold; padding-bottom: 20px; padding-left: 20px;")
        layout.addWidget(logo_label)
        
        # Navigation Buttons
        self.btn_dashboard = self.create_nav_button("Dashboard", checked=True)
        self.btn_iphawk = self.create_nav_button("IPHawk")
        self.btn_portscope = self.create_nav_button("PortScope")
        self.btn_devicevault = self.create_nav_button("DeviceVault")
        self.btn_webpulse = self.create_nav_button("WebPulse")
        self.btn_netmap = self.create_nav_button("NetMap")
        self.btn_settings = self.create_nav_button("Settings")
        
        layout.addWidget(self.btn_dashboard)
        layout.addWidget(self.btn_iphawk)
        layout.addWidget(self.btn_portscope)
        layout.addWidget(self.btn_devicevault)
        layout.addWidget(self.btn_webpulse)
        layout.addWidget(self.btn_netmap)
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        layout.addWidget(self.btn_settings)
        
    def create_nav_button(self, text, checked=False):
        btn = QPushButton(text)
        btn.setCheckable(True)
        if checked:
            btn.setChecked(True)
        return btn
