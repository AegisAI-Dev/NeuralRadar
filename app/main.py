import sys
import os

# Add the parent directory to sys.path so 'app' is recognized as a package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import QApplication
from app.core.logger import setup_logger, logger
from app.core.config import load_config
from app.gui.main_window import MainWindow

def main():
    # Initialize logger
    setup_logger()
    logger.info("Starting NeuralRadar...")
    
    # Load configuration
    config = load_config()
    logger.info("Configuration loaded.")
    
    # Initialize PySide6 App
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("NeuralRadar")
    app.setOrganizationName("NeuralShield")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    logger.info("Application loop started.")
    # Run event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    # Fix for sys.argv running logic
    try:
        main()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)
