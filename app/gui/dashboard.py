from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QScrollArea, 
    QHBoxLayout, QSizePolicy, QSpacerItem, QPushButton
)
from PySide6.QtCore import Qt
from app.gui.theme import Theme


class StatCard(QFrame):
    """Compact stat card for the dashboard overview."""
    def __init__(self, label: str, value: str = "0", accent: str = None):
        super().__init__()
        c = Theme.COLORS
        accent = accent or c.PRIMARY
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {c.CARD};
                border: 1px solid {c.BORDER};
                border-radius: 10px;
                border-top: 3px solid {accent};
            }}
            QFrame:hover {{
                border-color: {accent};
                background-color: {c.CARD_HOVER};
            }}
        """)
        self.setFixedHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)
        
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {accent}; border: none;")
        layout.addWidget(self.value_label)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 12px; color: {c.MUTED}; letter-spacing: 0.5px; border: none;")
        layout.addWidget(lbl)
    
    def set_value(self, value: str):
        self.value_label.setText(value)


class ModuleCard(QFrame):
    """Premium module card for the elite NeuralShield dashboard."""
    def __init__(self, title: str, description: str, status: str = "Coming Soon", icon: str = ""):
        super().__init__()
        
        is_active = status == "Active"
        self.setStyleSheet(Theme.get_card_style(active=is_active))
        self.setFixedSize(290, 160)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)
        
        # Header with clean icon (only for active cards) and title
        header = QHBoxLayout()
        if icon and is_active:
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"font-size: 22px; color: {Theme.COLORS.PRIMARY}; border: none;")
            header.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 17px; font-weight: 600; color: {Theme.COLORS.TEXT_BRIGHT}; border: none;")
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
        desc_label.setStyleSheet(f"color: {Theme.COLORS.MUTED}; font-size: 13px; line-height: 1.45; border: none;")
        layout.addWidget(desc_label)
        
        layout.addStretch()


class Dashboard(QWidget):
    """Elite premium NeuralShield cyber-tech dashboard landing screen."""
    def __init__(self):
        super().__init__()
        Theme.apply_theme(self)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 36, 40, 36)
        main_layout.setSpacing(28)
        
        # === HERO SECTION ===
        hero = QVBoxLayout()
        hero.setSpacing(10)
        
        title = QLabel("NeuralRadar")
        title.setStyleSheet(f"font-size: 42px; font-weight: 700; color: {Theme.COLORS.PRIMARY}; letter-spacing: -1px;")
        hero.addWidget(title)
        
        subtitle = QLabel("Local-first network discovery, inventory and visibility platform.")
        subtitle.setStyleSheet(f"color: {Theme.COLORS.TEXT}; font-size: 17px; font-weight: 400;")
        hero.addWidget(subtitle)
        
        # Metadata
        meta = QLabel("NeuralShield  •  Created by 0xRootNull")
        meta.setStyleSheet(f"color: {Theme.COLORS.MUTED}; font-size: 12px; letter-spacing: 0.5px;")
        hero.addWidget(meta)
        
        # Privacy strip
        privacy_strip = QLabel("LOCAL-FIRST  •  NO TELEMETRY  •  PERMISSION-BASED SCANNING")
        privacy_strip.setStyleSheet(f"""
            background-color: {Theme.COLORS.CARD}; 
            color: {Theme.COLORS.PRIMARY_DIM}; 
            padding: 12px 24px; 
            border-radius: 8px;
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 1.5px;
            border: 1px solid {Theme.COLORS.BORDER};
        """)
        privacy_strip.setWordWrap(True)
        hero.addWidget(privacy_strip)
        
        main_layout.addLayout(hero)
        
        # === BASIC STATS ===
        stats_header = QLabel("OVERVIEW")
        stats_header.setStyleSheet(Theme.section_title_style())
        main_layout.addWidget(stats_header)
        
        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)
        
        c = Theme.COLORS
        self.stat_devices = StatCard("Total Devices", "—", c.PRIMARY)
        self.stat_services = StatCard("Open Services", "—", c.NEURAL_BLUE)
        self.stat_endpoints = StatCard("Web Endpoints", "—", c.PURPLE)
        self.stat_online = StatCard("Online Now", "—", c.SUCCESS)
        
        stats_row.addWidget(self.stat_devices)
        stats_row.addWidget(self.stat_services)
        stats_row.addWidget(self.stat_endpoints)
        stats_row.addWidget(self.stat_online)
        stats_row.addStretch()
        
        main_layout.addLayout(stats_row)
        
        # Refresh button
        refresh_row = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Stats")
        self.btn_refresh.setStyleSheet(Theme.secondary_btn_style())
        self.btn_refresh.clicked.connect(self.refresh_stats)
        refresh_row.addWidget(self.btn_refresh)
        refresh_row.addStretch()
        main_layout.addLayout(refresh_row)
        
        # === SCROLLABLE CONTENT ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(24)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # === CORE MODULES ===
        active_header = QLabel("CORE MODULES")
        active_header.setStyleSheet(Theme.section_title_style())
        scroll_layout.addWidget(active_header)
        
        grid = QGridLayout()
        grid.setSpacing(20)
        grid.setContentsMargins(0, 0, 0, 0)
        
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
            if col > 1:
                col = 0
                row += 1
        
        scroll_layout.addLayout(grid)
        
        # === QUICK ACTIONS ===
        qa_header = QLabel("QUICK ACTIONS")
        qa_header.setStyleSheet(Theme.section_title_style())
        scroll_layout.addWidget(qa_header)
        
        qa_frame = QFrame()
        qa_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.COLORS.CARD};
                border: 1px solid {Theme.COLORS.BORDER};
                border-radius: 10px;
            }}
        """)
        qa_layout = QVBoxLayout(qa_frame)
        qa_layout.setContentsMargins(24, 20, 24, 20)
        qa_layout.setSpacing(8)
        
        actions = [
            "→  Navigate to IPHawk to discover devices on your network",
            "→  Use PortScope to identify open TCP services on discovered hosts",
            "→  Run WebPulse to check HTTP/HTTPS metadata and TLS status",
            "→  View DeviceVault for your persistent local asset inventory",
        ]
        for text in actions:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {Theme.COLORS.MUTED}; font-size: 13px; border: none;")
            qa_layout.addWidget(lbl)
        
        scroll_layout.addWidget(qa_frame)
        
        # === ROADMAP ===
        coming_header = QLabel("ROADMAP")
        coming_header.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {Theme.COLORS.MUTED}; letter-spacing: 2px; border: none;")
        scroll_layout.addWidget(coming_header)
        
        roadmap_grid = QGridLayout()
        roadmap_grid.setSpacing(20)
        roadmap_grid.setContentsMargins(0, 0, 0, 0)
        
        coming_modules = [
            ("NetMap", "Visual network mapping.", "Coming Soon", ""),
            ("WatchTower", "Uptime monitoring.", "Coming Soon", ""),
            ("ShieldAudit", "Defensive security insights.", "Coming Soon", ""),
            ("ContainerRadar", "Docker, LXC and Proxmox overview.", "Coming Soon", ""),
        ]
        
        r_row = r_col = 0
        for title, desc, status, icon in coming_modules:
            card = ModuleCard(title, desc, status, icon)
            roadmap_grid.addWidget(card, r_row, r_col)
            r_col += 1
            if r_col > 3:
                r_col = 0
                r_row += 1
        
        scroll_layout.addLayout(roadmap_grid)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area, stretch=1)
    
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_stats()
    
    def refresh_stats(self):
        """Refresh dashboard stats from DeviceVault (local DB only, no network calls)."""
        try:
            from app.core.database import SessionLocal
            from app.modules.devicevault.service import DeviceVaultService
            db = SessionLocal()
            try:
                devices = DeviceVaultService.get_all_devices(db)
                total = len(devices)
                online = sum(1 for d in devices if d.status == "Online")
                
                self.stat_devices.set_value(str(total))
                self.stat_online.set_value(str(online))
                
                # Services count
                try:
                    svc_count = 0
                    for d in devices:
                        svcs = DeviceVaultService.get_device_services(db, d.id)
                        svc_count += len(svcs)
                    self.stat_services.set_value(str(svc_count))
                except Exception:
                    self.stat_services.set_value("—")
                
                # Web endpoints count
                try:
                    web_count = 0
                    for d in devices:
                        try:
                            webs = DeviceVaultService.get_device_web_services(db, d.id)
                            web_count += len(webs)
                        except Exception:
                            pass
                    self.stat_endpoints.set_value(str(web_count))
                except Exception:
                    self.stat_endpoints.set_value("—")
                    
            finally:
                db.close()
        except Exception:
            self.stat_devices.set_value("—")
            self.stat_services.set_value("—")
            self.stat_endpoints.set_value("—")
            self.stat_online.set_value("—")
