from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from app.core.version import VERSION

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        title = QLabel("Settings / About")
        title.setStyleSheet("color: #cdd6f4; font-size: 28px; font-weight: bold;")
        layout.addWidget(title)
        
        # About Section
        about_frame = QFrame()
        about_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border: 1px solid #313244;
                border-radius: 8px;
            }
        """)
        about_layout = QVBoxLayout(about_frame)
        about_layout.setContentsMargins(20, 20, 20, 20)
        about_layout.setSpacing(10)
        
        version_label = QLabel(f"NeuralRadar {VERSION}")
        version_label.setStyleSheet("color: #89b4fa; font-size: 20px; font-weight: bold; border: none;")
        about_layout.addWidget(version_label)
        
        built_by = QLabel("Built by NeuralShield")
        built_by.setStyleSheet("color: #a6adc8; font-size: 14px; border: none;")
        about_layout.addWidget(built_by)
        
        created_by = QLabel("Created by 0xRootNull")
        created_by.setStyleSheet("color: #a6adc8; font-size: 14px; border: none;")
        about_layout.addWidget(created_by)
        
        platform_info = QLabel("Local-first network visibility platform")
        platform_info.setStyleSheet("color: #cdd6f4; font-size: 14px; border: none; margin-top: 10px;")
        about_layout.addWidget(platform_info)
        
        layout.addWidget(about_frame)
        
        # Safety Note
        safety_frame = QFrame()
        safety_frame.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-left: 4px solid #f38ba8;
                border-radius: 4px;
            }
        """)
        safety_layout = QVBoxLayout(safety_frame)
        safety_layout.setContentsMargins(15, 15, 15, 15)
        
        safety_title = QLabel("⚠️ Safety Notice")
        safety_title.setStyleSheet("color: #f38ba8; font-size: 16px; font-weight: bold; border: none;")
        safety_layout.addWidget(safety_title)
        
        safety_text = QLabel("Only scan systems you own or have permission to test.")
        safety_text.setStyleSheet("color: #cdd6f4; font-size: 14px; border: none;")
        safety_layout.addWidget(safety_text)
        
        layout.addWidget(safety_frame)
        
        # Privacy Note
        privacy_frame = QFrame()
        privacy_frame.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-left: 4px solid #a6e3a1;
                border-radius: 4px;
            }
        """)
        privacy_layout = QVBoxLayout(privacy_frame)
        privacy_layout.setContentsMargins(15, 15, 15, 15)
        
        privacy_title = QLabel("🔒 Privacy Notice")
        privacy_title.setStyleSheet("color: #a6e3a1; font-size: 16px; font-weight: bold; border: none;")
        privacy_layout.addWidget(privacy_title)
        
        privacy_text = QLabel("NeuralRadar stores data locally and does not send telemetry.")
        privacy_text.setStyleSheet("color: #cdd6f4; font-size: 14px; border: none;")
        privacy_layout.addWidget(privacy_text)
        
        layout.addWidget(privacy_frame)
        
        # Fill remaining space
        layout.addStretch(1)
