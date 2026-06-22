import os
import sys

def is_packaged():
    """Check if the application is running as a PyInstaller packaged executable."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def get_app_data_dir():
    """
    Get the base application data directory.
    If packaged, returns %LOCALAPPDATA%/NeuralRadar.
    If in dev mode, returns the project root.
    """
    if is_packaged():
        local_app_data = os.getenv('LOCALAPPDATA')
        if not local_app_data:
            # Fallback if LOCALAPPDATA is missing for some reason
            local_app_data = os.path.expanduser('~\\AppData\\Local')
        return os.path.join(local_app_data, 'NeuralRadar')
    else:
        # Assuming app/core/paths.py, project root is 3 levels up
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def get_data_dir():
    """Get the path to the data folder."""
    data_dir = os.path.join(get_app_data_dir(), 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def get_database_path():
    """Get the path to the SQLite database file."""
    return os.path.join(get_data_dir(), 'neuralradar.db')

def get_logs_dir():
    """Get the path to the logs folder."""
    logs_dir = os.path.join(get_app_data_dir(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def get_log_file_path():
    """Get the path to the main log file."""
    return os.path.join(get_logs_dir(), 'neuralradar.log')


def get_filter_presets_path():
    """Get the path to the DeviceVault filter presets JSON file.
    Uses the shared data directory for both dev and packaged modes.
    """
    return os.path.join(get_data_dir(), 'devicevault_filter_presets.json')
