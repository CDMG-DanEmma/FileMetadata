import sys
import logging
import os
from PyQt6.QtWidgets import QApplication
from gui_main_window import MainWindow
from utils_path_manager import PathManager
from utils_metadata_manager import MetadataManager
from utils_access_safety import AccessSafety
from config import Config

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        filename='file_navigator.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def check_dependencies():
    """Verify all required dependencies are available"""
    required_packages = ['PyQt6', 'pandas', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise ImportError(f"Missing required packages: {', '.join(missing_packages)}")

def initialize_safety(config):
    """Initialize access safety controls"""
    safety = AccessSafety()
    protected_paths = [
        config['network_paths']['root'],
        config['network_paths']['projects'],
        config['network_paths']['templates']
    ]
    safety.set_protected_paths(protected_paths)
    return safety

def initialize_application():
    """Initialize core application components"""
    config = Config()  # Create Config instance directly
    
    # Initialize path manager
    path_manager = PathManager()
    path_manager.verify_network_paths(config.get_network_paths())
    
    # Initialize safety system
    safety = AccessSafety()
    protected_paths = [
        config.get_network_paths()['root'],
        config.get_network_paths()['projects'],
        config.get_network_paths()['templates']
    ]
    safety.set_protected_paths(protected_paths)
    
    # Initialize metadata
    metadata_path = os.path.join("local_metadata", "metadata.xlsx")
    os.makedirs("local_metadata", exist_ok=True)
    metadata_manager = MetadataManager(safety, metadata_path)
    
    return config, safety

def main():
    """Main application entry point"""

    try:
        # Setup
        setup_logging()
        check_dependencies()
        
        # Initialize Qt Application
        app = QApplication(sys.argv)
        
        # Initialize core components with safety
        config, safety = initialize_application()
        
        # Create and show main window
        window = MainWindow(config, safety)  # Pass safety to MainWindow
        window.show()
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        logging.critical(f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()