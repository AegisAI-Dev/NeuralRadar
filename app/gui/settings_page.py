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
        main_layout.setSpacing(32)
        
        # Header
        header = QLabel("About NeuralRadar")
        header.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {Theme.COLORS.PRIMARY};")
        main_layout.addWidget(header)
        
        # Main info card
        info_card = QFrame()
        info_card.setStyleSheet(Theme.get_card_style(is_active=True))
        card_layout = QVBoxLayout(info_card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(24)
        
        # Branding
        brand_layout = QHBoxLayout()
        logo = QLabel("⚡")
        logo.setStyleSheet(f"font-size: 48px; color: {Theme.COLORS.PRIMARY};")
        brand_layout.addWidget(logo)
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(QLabel("NeuralRadar"))
        vlabel = QLabel(VERSION)
        vlabel.setStyleSheet(f"color: {Theme.COLORS.SECONDARY}; font-weight: bold;")
        title_layout.addWidget(vlabel)
        brand_layout.addLayout(title_layout)
        brand_layout.addStretch()
        
        card_layout.addLayout(brand_layout)
        
        # Description
        desc = QLabel("Local-first network visibility platform for security professionals and researchers.")
        desc.setWordWrap(True)
        desc.setStyleSheet(f"font-size: 15px; color: {Theme.COLORS.TEXT_PRIMARY}; line-height: 1.5;")
        card_layout.addWidget(desc)
        
        # Key facts in grid
        facts_grid = QGridLayout()
        facts_grid.setSpacing(16)
        
        facts = [
            ("Company", "NeuralShield"),
            ("Author", "0xRootNull"),
            ("Version", VERSION),
            ("Architecture", "Python + PySide6 • PyInstaller packaged"),
            ("Data Storage", "%LOCALAPPDATA%\\NeuralRadar (persistent across runs)"),
        ]
        
        for i, (label, value) in enumerate(facts):
            lbl = QLabel(f"<b>{label}:</b>")
            lbl.setStyleSheet(f"color: {Theme.COLORS.TEXT_MUTED};")
            val = QLabel(value)
            val.setStyleSheet(f"color: {Theme.COLORS.TEXT_PRIMARY};")
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
        modules_label = QLabel("Currently Available Modules")
        modules_label.setStyleSheet(f"font-weight: 600; color: {Theme.COLORS.PRIMARY}; padding-top: 8px;")
        card_layout.addWidget(modules_label)
        
        modules_text = QLabel("• IPHawk — Network discovery\n• DeviceVault — Asset inventory\n• PortScope — Service & port mapping\n• WebPulse — Web metadata & TLS inspection")
        modules_text.setStyleSheet(f"color: {Theme.COLORS.TEXT_MUTED}; font-family: monospace; padding: 12px; background-color: rgba(0,0,0,0.2); border-radius: 6px;")
        card_layout.addWidget(modules_text)
        
        main_layout.addWidget(info_card)
        main_layout.addStretch()
        
    def _create_info_section(self, title: str, content: str) -> QFrame:
        """Helper to create consistent info panels."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.COLORS.BG_CARD};
                border: 1px solid {Theme.COLORS.BORDER};
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {Theme.COLORS.PRIMARY}; font-size: 16px; font-weight: 600;")
        layout.addWidget(title_label)
        
        content_label = QLabel(content)
        content_label.setStyleSheet(f"color: {Theme.COLORS.TEXT_MUTED}; line-height: 1.6;")
        layout.addWidget(content_label)
        
        return frame
