from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from app.gui.sidebar import Sidebar
from app.gui.dashboard import Dashboard
from app.gui.iphawk_page import IPHawkPage
from app.gui.devicevault_page import DeviceVaultPage
from app.gui.portscope_page import PortScopePage
from app.gui.webpulse_page import WebPulsePage
from app.gui.netmap_page import NetMapPage
from app.gui.theme import Theme
from app.core.logger import logger
from app.core.version import VERSION
from app.gui.settings_page import SettingsPage


class PlaceholderPage(QWidget):
    """Simple placeholder for coming-soon modules with theme support."""
    def __init__(self, title: str):
        super().__init__()
        layout = QHBoxLayout(self)
        label = QLabel(f"{title} Module — Coming Soon")
        label.setStyleSheet(f"color: {Theme.COLORS.TEXT_MUTED}; font-size: 24px; font-style: italic;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)


class MainWindow(QMainWindow):
    """Main application window with polished cyber-tech interface."""
    def __init__(self):
        super().__init__()
        
        # Professional branding title
        self.setWindowTitle(f"NeuralRadar {VERSION}")
        self.setMinimumSize(1200, 800)
        
        # Apply the centralized professional theme
        Theme.apply_theme(self)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar with updated styling
        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)
        
        # Content area (stacked pages)
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("background-color: transparent;")
        self.main_layout.addWidget(self.content_area, stretch=5)
        
        # Initialize pages (order defines navigation indices)
        self.dashboard_page = Dashboard()
        self.content_area.addWidget(self.dashboard_page)
        
        self.iphawk_page = IPHawkPage()
        self.content_area.addWidget(self.iphawk_page)
        
        self.portscope_page = PortScopePage()
        self.content_area.addWidget(self.portscope_page)
        
        self.devicevault_page = DeviceVaultPage()
        self.content_area.addWidget(self.devicevault_page)
        
        self.webpulse_page = WebPulsePage()
        self.content_area.addWidget(self.webpulse_page)
        
        self.netmap_page = NetMapPage()
        self.content_area.addWidget(self.netmap_page)
        
        self.settings_page = SettingsPage()
        self.content_area.addWidget(self.settings_page)
        
        # Connect navigation (must match page add order)
        self.sidebar.btn_dashboard.clicked.connect(lambda: self.switch_page(0, self.sidebar.btn_dashboard))
        self.sidebar.btn_iphawk.clicked.connect(lambda: self.switch_page(1, self.sidebar.btn_iphawk))
        self.sidebar.btn_portscope.clicked.connect(lambda: self.switch_page(2, self.sidebar.btn_portscope))
        self.sidebar.btn_devicevault.clicked.connect(lambda: self.switch_page(3, self.sidebar.btn_devicevault))
        self.sidebar.btn_webpulse.clicked.connect(lambda: self.switch_page(4, self.sidebar.btn_webpulse))
        self.sidebar.btn_netmap.clicked.connect(lambda: self.switch_page(5, self.sidebar.btn_netmap))
        self.sidebar.btn_settings.clicked.connect(lambda: self.switch_page(6, self.sidebar.btn_settings))
        
        self.nav_buttons = [
            self.sidebar.btn_dashboard,
            self.sidebar.btn_iphawk,
            self.sidebar.btn_portscope,
            self.sidebar.btn_devicevault,
            self.sidebar.btn_webpulse,
            self.sidebar.btn_netmap,
            self.sidebar.btn_settings
        ]
        
        # Default to dashboard
        self.sidebar.btn_dashboard.setChecked(True)
        
        logger.info("MainWindow initialized with NeuralShield cyber-tech branding and theme.")
        
    def switch_page(self, index: int, button):
        """Switch displayed page and update active navigation button state."""
        self.content_area.setCurrentIndex(index)
        for btn in self.nav_buttons:
            if btn != button:
                btn.setChecked(False)
        button.setChecked(True)
