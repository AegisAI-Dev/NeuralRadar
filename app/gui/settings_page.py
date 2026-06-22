from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QGridLayout
from PySide6.QtCore import Qt
from app.gui.theme import Theme
from app.core.version import VERSION


class SettingsPage(QWidget):
    """Professional About / Information page with NeuralShield branding."""
    def __init__(self):
        super().__init__()
        Theme.apply_theme(self)  # Apply centralized styling
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(28)
        
        # Header
        header = QLabel("About NeuralRadar")
        header.setStyleSheet(f"font-size: 32px; font-weight: 700; color: {Theme.COLORS.PRIMARY};")
        main_layout.addWidget(header)
        
        # Main info card
        info_card = QFrame()
        info_card.setStyleSheet(Theme.get_card_style(is_active=True))
        card_layout = QVBoxLayout(info_card)
        card_layout.setContentsMargins(32, 28, 32, 28)
        card_layout.setSpacing(20)
        
        # Branding
        brand_layout = QHBoxLayout()
        logo = QLabel("⚡")
        logo.setStyleSheet(f"font-size: 42px; color: {Theme.COLORS.PRIMARY}; border: none;")
        brand_layout.addWidget(logo)
        
        title_layout = QVBoxLayout()
        app_name = QLabel("NeuralRadar")
        app_name.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {Theme.COLORS.TEXT_BRIGHT}; border: none;")
        title_layout.addWidget(app_name)
        vlabel = QLabel(VERSION)
        vlabel.setStyleSheet(f"color: {Theme.COLORS.SECONDARY}; font-weight: 600; font-size: 14px; border: none;")
        title_layout.addWidget(vlabel)
        brand_layout.addLayout(title_layout)
        brand_layout.addStretch()
        
        card_layout.addLayout(brand_layout)
        
        # Description
        desc = QLabel("Local-first network visibility platform for security professionals and researchers.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 15px; color: {Theme.COLORS.TEXT}; line-height: 1.5; border: none;")
        card_layout.addWidget(desc)
        
        # Key facts in grid
        facts_grid = QGridLayout()
        facts_grid.setSpacing(14)
        
        facts = [
            ("Company", "NeuralShield"),
            ("Author", "0xRootNull"),
            ("Version", VERSION),
            ("Architecture", "Python + PySide6 • PyInstaller packaged"),
            ("Data Storage", "%LOCALAPPDATA%\\NeuralRadar (persistent across runs)"),
        ]
        
        for i, (label, value) in enumerate(facts):
            lbl = QLabel(f"<b>{label}:</b>")
            lbl.setStyleSheet(f"color: {Theme.COLORS.MUTED}; border: none; font-size: 13px;")
            val = QLabel(value)
            val.setStyleSheet(f"color: {Theme.COLORS.TEXT}; border: none; font-size: 13px;")
            facts_grid.addWidget(lbl, i, 0)
            facts_grid.addWidget(val, i, 1)
        
        card_layout.addLayout(facts_grid)
        
        # Privacy & Safety sections
        privacy_card = self._create_info_section(
            "🔒 Privacy & Security", 
            "• No telemetry\n• No cloud sync or external API calls\n• All data remains on your local machine\n• SQLite database in user AppData"
        )
        safety_card = self._create_info_section(
            "🛡️ Responsible Usage", 
            "Only scan networks and systems you own or have explicit written permission to test.\n\nUnauthorized scanning may violate laws and ethical guidelines."
        )
        
        card_layout.addWidget(privacy_card)
        card_layout.addWidget(safety_card)
        
        # Current modules
        modules_label = QLabel("CURRENTLY AVAILABLE MODULES")
        modules_label.setStyleSheet(Theme.section_title_style())
        card_layout.addWidget(modules_label)
        
        modules_text = QLabel("• IPHawk — Network discovery\n• DeviceVault — Asset inventory\n• PortScope — Service & port mapping\n• WebPulse — Web metadata & TLS inspection")
        modules_text.setStyleSheet(f"""
            color: {Theme.COLORS.MUTED};
            font-family: monospace;
            padding: 14px;
            background-color: {Theme.COLORS.SURFACE};
            border: 1px solid {Theme.COLORS.BORDER};
            border-radius: 8px;
            font-size: 13px;
            line-height: 1.6;
        """)
        card_layout.addWidget(modules_text)
        
        main_layout.addWidget(info_card)
        main_layout.addStretch()
        
    def _create_info_section(self, title: str, content: str) -> QFrame:
        """Helper to create consistent info panels."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.COLORS.SURFACE};
                border: 1px solid {Theme.COLORS.BORDER};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {Theme.COLORS.PRIMARY_DIM}; font-size: 15px; font-weight: 600; border: none;")
        layout.addWidget(title_label)
        
        content_label = QLabel(content)
        content_label.setStyleSheet(f"color: {Theme.COLORS.MUTED}; line-height: 1.6; border: none; font-size: 13px;")
        layout.addWidget(content_label)
        
        return frame
