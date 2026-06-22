from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy, QFrame, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from app.gui.theme import Theme
from app.core.version import VERSION


class Sidebar(QWidget):
    """Professional sidebar with NeuralShield branding and cyber-tech styling."""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(240)
        
        # Apply theme stylesheet for sidebar and nav buttons
        self.setStyleSheet(Theme.get_sidebar_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 28, 16, 20)
        layout.setSpacing(4)
        
        # === BRANDING HEADER ===
        logo_container = QFrame()
        logo_container.setObjectName("LogoContainer")
        logo_container.setStyleSheet("border: none; background: transparent;")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(8, 0, 8, 8)
        logo_layout.setSpacing(2)
        
        logo_label = QLabel("NEURALRADAR")
        logo_label.setObjectName("Logo")
        logo_label.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        logo_layout.addWidget(logo_label)
        
        subtitle = QLabel("NEURALSHIELD")
        subtitle.setObjectName("Subtitle")
        subtitle.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
        logo_layout.addWidget(subtitle)
        
        layout.addWidget(logo_container)
        
        # Version badge
        version_frame = QFrame()
        version_frame.setStyleSheet("background: transparent; border: none;")
        version_layout = QHBoxLayout(version_frame)
        version_layout.setContentsMargins(12, 0, 12, 8)
        
        version_badge = QLabel(f"{VERSION}")
        version_badge.setObjectName("VersionBadge")
        version_layout.addWidget(version_badge)
        version_layout.addStretch()
        
        layout.addWidget(version_frame)
        
        # Divider
        divider = QFrame()
        divider.setObjectName("SidebarDivider")
        divider.setFixedHeight(1)
        layout.addWidget(divider)
        
        # Section label
        modules_label = QLabel("MODULES")
        modules_label.setObjectName("SectionLabel")
        layout.addWidget(modules_label)
        
        # Navigation
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
        
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        # System section
        sys_label = QLabel("SYSTEM")
        sys_label.setObjectName("SectionLabel")
        layout.addWidget(sys_label)
        
        layout.addWidget(self.btn_settings)
        
        # Footer tagline
        tagline = QLabel("Local-first · Secure · Transparent")
        tagline.setStyleSheet(f"color: {Theme.COLORS.MUTED}; font-size: 10px; padding-top: 16px; border: none; background: transparent;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tagline)
        
    def create_nav_button(self, text: str, checked: bool = False) -> QPushButton:
        """Create styled navigation button with proper object name for theming."""
        btn = QPushButton(text)
        btn.setObjectName("navButton")
        btn.setCheckable(True)
        btn.setChecked(checked)
        btn.setProperty("nav", True)
        return btn
