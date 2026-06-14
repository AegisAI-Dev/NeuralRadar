from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from app.gui.sidebar import Sidebar
from app.gui.dashboard import Dashboard
from app.gui.iphawk_page import IPHawkPage
from app.gui.devicevault_page import DeviceVaultPage
from app.core.logger import logger

class PlaceholderPage(QWidget):
    def __init__(self, title):
        super().__init__()
        layout = QHBoxLayout(self)
        label = QLabel(f"{title} Module - Coming Soon")
        label.setStyleSheet("color: #a6adc8; font-size: 24px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("NeuralRadar - Network Visibility Platform")
        self.setMinimumSize(1100, 750)
        self.setStyleSheet("background-color: #181825;")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)
        
        # Content Area
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)
        
        # Pages
        self.dashboard_page = Dashboard()
        self.content_area.addWidget(self.dashboard_page)
        
        self.iphawk_page = IPHawkPage()
        self.content_area.addWidget(self.iphawk_page)
        
        self.portscope_page = PlaceholderPage("PortScope")
        self.content_area.addWidget(self.portscope_page)
        
        self.devicevault_page = DeviceVaultPage()
        self.content_area.addWidget(self.devicevault_page)
        
        self.netmap_page = PlaceholderPage("NetMap")
        self.content_area.addWidget(self.netmap_page)
        
        self.settings_page = PlaceholderPage("Settings")
        self.content_area.addWidget(self.settings_page)
        
        # Connect sidebar buttons
        self.sidebar.btn_dashboard.clicked.connect(lambda: self.switch_page(0, self.sidebar.btn_dashboard))
        self.sidebar.btn_iphawk.clicked.connect(lambda: self.switch_page(1, self.sidebar.btn_iphawk))
        self.sidebar.btn_portscope.clicked.connect(lambda: self.switch_page(2, self.sidebar.btn_portscope))
        self.sidebar.btn_devicevault.clicked.connect(lambda: self.switch_page(3, self.sidebar.btn_devicevault))
        self.sidebar.btn_netmap.clicked.connect(lambda: self.switch_page(4, self.sidebar.btn_netmap))
        self.sidebar.btn_settings.clicked.connect(lambda: self.switch_page(5, self.sidebar.btn_settings))
        
        # Keep track of buttons for easy unchecking
        self.nav_buttons = [
            self.sidebar.btn_dashboard,
            self.sidebar.btn_iphawk,
            self.sidebar.btn_portscope,
            self.sidebar.btn_devicevault,
            self.sidebar.btn_netmap,
            self.sidebar.btn_settings
        ]
        
        logger.info("MainWindow initialized.")
        
    def switch_page(self, index, button):
        self.content_area.setCurrentIndex(index)
        for btn in self.nav_buttons:
            if btn != button:
                btn.setChecked(False)
        button.setChecked(True)
