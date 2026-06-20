from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QScrollArea, 
    QHBoxLayout, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt
from app.gui.theme import Theme


class ModuleCard(QFrame):
    """Premium module card for the elite NeuralShield dashboard."""
    def __init__(self, title: str, description: str, status: str = "Coming Soon", icon: str = ""):
        super().__init__()
        
        is_active = status == "Active"
        self.setStyleSheet(Theme.get_card_style(active=is_active))
        self.setFixedSize(290, 170)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)
        
        # Header with clean icon (only for active cards) and title
        header = QHBoxLayout()
        if icon and is_active:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"font-size: 26px; color: {Theme.COLORS.PRIMARY};")
            header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #E5E7EB;")
        header.addWidget(title_label)
        header.addStretch()
        
        # Status badge
        status_label = QLabel(status)
        status_label.setProperty("status", "active" if is_active else "coming-soon")
        status_label.setStyleSheet("")  # Uses global theme
        header.addWidget(status_label)
        
        layout.addLayout(header)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #94A3B8; font-size: 13px; line-height: 1.45;")
        layout.addWidget(desc_label)
        
        layout.addStretch()


class Dashboard(QWidget):
    """Elite premium NeuralShield cyber-tech dashboard landing screen."""
    def __init__(self):
        super().__init__()
        Theme.apply_theme(self)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(36)
        
        # === PREMIUM HERO SECTION ===
        hero = QVBoxLayout()
        hero.setSpacing(14)
        
        title = QLabel("NeuralRadar")
        title.setStyleSheet(f"font-size: 52px; font-weight: 700; color: {Theme.COLORS.PRIMARY}; letter-spacing: -1.5px;")
        hero.addWidget(title)
        
        subtitle = QLabel("Local-first network discovery, inventory and visibility platform.")
        subtitle.setStyleSheet(f"color: {Theme.COLORS.TEXT}; font-size: 19px; font-weight: 400; max-width: 680px;")
        hero.addWidget(subtitle)
        
        # Metadata line
        meta = QLabel("NeuralShield • v0.1-alpha • Created by 0xRootNull")
        meta.setStyleSheet(f"color: {Theme.COLORS.MUTED}; font-size: 12px; letter-spacing: 0.5px;")
        hero.addWidget(meta)
        
        # Safety/privacy strip
        privacy_strip = QLabel("LOCAL-FIRST  •  NO TELEMETRY  •  PERMISSION-BASED SCANNING")
        privacy_strip.setStyleSheet(f"""
            background-color: #0F172A; 
            color: #38BDF8; 
            padding: 14px 28px; 
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            letter-spacing: 1.5px;
            border: 1px solid #26364F;
        """)
        privacy_strip.setWordWrap(True)
        hero.addWidget(privacy_strip)
        
        main_layout.addLayout(hero)
        
        # Core active modules section
        active_header = QLabel("CORE MODULES")
        active_header.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {Theme.COLORS.PRIMARY}; letter-spacing: 2px; padding: 8px 0 4px;")
        main_layout.addWidget(active_header)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        grid = QGridLayout(scroll_content)
        grid.setSpacing(28)
        grid.setContentsMargins(0, 0, 0, 0)
        
        # Active cards with exact symbols and descriptions
        active_modules = [
            ("IPHawk", "Discover active devices on local networks.", "Active", "◉"),
            ("DeviceVault", "Store and manage local asset inventory.", "Active", "▣"),
            ("PortScope", "Identify open TCP services safely.", "Active", "⟡"),
            ("WebPulse", "Check HTTP/HTTPS metadata safely.", "Active", "◌"),
        ]
        
        row = col = 0
        for title, desc, status, icon in active_modules:
            card = ModuleCard(title, desc, status, icon)
            grid.addWidget(card, row, col)
            col += 1
            if col > 1:  # 2-column for active to give breathing room
                col = 0
                row += 1
        
        # Coming soon section
        coming_header = QLabel("ROADMAP")
        coming_header.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {Theme.COLORS.MUTED}; letter-spacing: 2px; padding: 24px 0 4px;")
        main_layout.addWidget(coming_header)
        
        coming_modules = [
            ("NetMap", "Visual network mapping.", "Coming Soon", ""),
            ("WatchTower", "Uptime monitoring.", "Coming Soon", ""),
            ("ShieldAudit", "Defensive security insights.", "Coming Soon", ""),
            ("ContainerRadar", "Docker, LXC and Proxmox overview.", "Coming Soon", ""),
        ]
        
        for title, desc, status, icon in coming_modules:
            card = ModuleCard(title, desc, status, icon)
            grid.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, stretch=1)
        main_layout.addStretch()
