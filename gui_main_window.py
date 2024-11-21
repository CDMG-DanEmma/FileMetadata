from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QMenuBar, QStatusBar, QToolBar, QMessageBox,
                            QFileDialog, QLabel)
from PyQt6.QtCore import Qt
import logging
import os
from gui_search_panel import SearchPanel
from gui_file_tree import FileTreeView
from gui_metadata_editor import MetadataEditor
from utils_metadata_manager import MetadataManager

class MainWindow(QMainWindow):
    def __init__(self, config, safety_manager):
        super().__init__()
        self.config = config
        self.safety = safety_manager
        try:
            # Initialize metadata manager
            metadata_path = os.path.join("local_metadata", "metadata.xlsx")
            os.makedirs("local_metadata", exist_ok=True)
            self.metadata_manager = MetadataManager(self.safety, metadata_path)
            
            # Setup UI
            self.setup_ui()
            self.setup_menubar()
            self.setup_toolbar()
            self.setup_statusbar()
            self.setup_styles()
            self.load_window_state()
            self.connect_signals()
            self.load_initial_directory()
            
            # Show initial statistics
            self.update_status_statistics()
        except Exception as e:
            logging.error(f"Error initializing MainWindow: {str(e)}")
            raise

    def setup_ui(self):
        """Initialize main UI components"""
        try:
            self.setWindowTitle("Project File Navigator")
            self.resize(1200, 800)
            
            # Central widget and layout
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.layout = QVBoxLayout(self.central_widget)
            self.layout.setContentsMargins(6, 6, 6, 6)
            
            # Create main UI components
            self.setup_splitter()
        except Exception as e:
            logging.error(f"Error in setup_ui: {str(e)}")
            raise

    def setup_splitter(self):
        """Create split view for file tree and metadata"""
        try:
            self.splitter = QSplitter(Qt.Orientation.Horizontal)
            
            # Left side: File tree and search
            self.left_widget = QWidget()
            self.left_layout = QVBoxLayout(self.left_widget)
            self.left_layout.setContentsMargins(0, 0, 0, 0)
            
            # Initialize search panel
            self.search_panel = SearchPanel(self)
            self.left_layout.addWidget(self.search_panel)
            
            # Initialize file tree
            self.file_tree = FileTreeView(self.safety, self)
            self.left_layout.addWidget(self.file_tree)
            
            # Right side: Metadata panel
            self.metadata_editor = MetadataEditor(self.safety, self)
            
            # Add widgets to splitter
            self.splitter.addWidget(self.left_widget)
            self.splitter.addWidget(self.metadata_editor)
            
            # Add splitter to main layout
            self.layout.addWidget(self.splitter)
            
            # Set initial splitter position
            self.splitter.setSizes([int(self.width() * 0.6), int(self.width() * 0.4)])
            
        except Exception as e:
            logging.error(f"Error in setup_splitter: {str(e)}")
            raise

    def setup_menubar(self):
        """Create application menu bar"""
        try:
            self.menubar = self.menuBar()
            
            # File menu
            file_menu = self.menubar.addMenu("&File")
            file_menu.addAction("Open Project Folder", self.open_project_folder)
            file_menu.addAction("Refresh", self.refresh_view)
            file_menu.addAction("Open Metadata Excel", self.open_metadata_excel)
            file_menu.addSeparator()
            file_menu.addAction("Exit", self.close)
            
            # View menu
            view_menu = self.menubar.addMenu("&View")
            view_menu.addAction("Refresh", self.refresh_view)
            view_menu.addAction("Show Statistics", self.show_statistics)
            
            # Tools menu
            tools_menu = self.menubar.addMenu("&Tools")
            tools_menu.addAction("Add Selected Files to Database", self.add_selected_to_database)
            tools_menu.addAction("Clear Metadata Cache", self.clear_metadata_cache)
            
            # Help menu
            help_menu = self.menubar.addMenu("&Help")
            help_menu.addAction("About", self.show_about)
            
        except Exception as e:
            logging.error(f"Error in setup_menubar: {str(e)}")
            raise

    def setup_toolbar(self):
        """Create main toolbar"""
        try:
            self.toolbar = QToolBar()
            self.addToolBar(self.toolbar)
            
            # Add toolbar actions
            self.toolbar.addAction("Refresh", self.refresh_view)
            self.toolbar.addAction("Add to Database", self.add_selected_to_database)
            
            # Add statistics label
            self.stats_label = QLabel()
            self.toolbar.addWidget(self.stats_label)
            
        except Exception as e:
            logging.error(f"Error in setup_toolbar: {str(e)}")
            raise

    def setup_statusbar(self):
        """Create status bar"""
        try:
            self.statusbar = QStatusBar()
            self.setStatusBar(self.statusbar)
            self.statusbar.showMessage("Ready")
        except Exception as e:
            logging.error(f"Error in setup_statusbar: {str(e)}")
            raise

    def setup_styles(self):
        """Setup application-wide styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTreeView {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3f3f3f;
            }
            QTreeView::item:hover {
                background-color: #363636;
            }
            QTreeView::item:selected {
                background-color: #404040;
            }
            QHeaderView::section {
                background-color: #323232;
                color: #ffffff;
                padding: 4px;
                border: none;
            }
            QPushButton {
                background-color: #404040;
                color: #ffffff;
                border: none;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QLabel {
                color: #ffffff;
            }
            QStatusBar {
                background-color: #323232;
                color: #ffffff;
            }
            QToolBar {
                background-color: #323232;
                border: none;
                spacing: 10px;
                padding: 5px;
            }
            QMenuBar {
                background-color: #323232;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #404040;
            }
        """)

    def connect_signals(self):
        """Connect all signal handlers"""
        try:
            # Connect search panel signals
            self.search_panel.searchRequested.connect(self.handle_search)
            self.search_panel.filterChanged.connect(self.apply_filters)
            
            # Connect file tree signals
            self.file_tree.fileSelected.connect(self.handle_file_selected)
            self.file_tree.filesAdded.connect(self.handle_files_added)
            
            # Connect metadata editor signals
            self.metadata_editor.metadataChanged.connect(self.handle_metadata_changed)
            
        except Exception as e:
            logging.error(f"Error connecting signals: {str(e)}")
            raise

    def load_initial_directory(self):
        """Load the initial directory into the file tree"""
        try:
            root_path = self.config.get_network_paths().get('root', os.path.expanduser('~'))
            if os.path.exists(root_path):
                self.file_tree.populate_tree(root_path)
                self.statusbar.showMessage(f"Loaded directory: {root_path}")
            else:
                fallback_path = os.path.expanduser('~')
                self.file_tree.populate_tree(fallback_path)
                self.statusbar.showMessage(f"Using fallback directory: {fallback_path}")
        except Exception as e:
            logging.error(f"Error loading initial directory: {str(e)}")
            self.show_error_message("Error", "Failed to load initial directory")

    def handle_search(self, search_text):
        """Handle search request"""
        try:
            self.statusbar.showMessage(f"Searching for: {search_text}")
            # Implement search functionality
        except Exception as e:
            logging.error(f"Error handling search: {str(e)}")
            self.show_error_message("Search Error", str(e))

    def apply_filters(self, filters):
        """Apply search filters"""
        try:
            self.statusbar.showMessage("Applying filters...")
            # Implement filter functionality
        except Exception as e:
            logging.error(f"Error applying filters: {str(e)}")
            self.show_error_message("Filter Error", str(e))

    def handle_file_selected(self, file_path):
        """Handle file selection"""
        try:
            self.statusbar.showMessage(f"Selected: {file_path}")
            metadata = self.metadata_manager.get_metadata(file_path)
            self.metadata_editor.load_file_metadata(file_path, metadata)
        except Exception as e:
            logging.error(f"Error handling file selection: {str(e)}")
            self.show_error_message("Selection Error", str(e))

    def handle_files_added(self, file_paths):
        """Handle adding files to metadata database"""
        try:
            if self.metadata_manager.add_files_basic_metadata(file_paths):
                self.statusbar.showMessage(f"Added {len(file_paths)} files to database")
                self.update_status_statistics()
            else:
                self.statusbar.showMessage("Failed to add files to database")
        except Exception as e:
            self.show_error_message("Error", f"Failed to add files: {str(e)}")

    def handle_metadata_changed(self, file_path, metadata):
        """Handle metadata updates"""
        try:
            if self.metadata_manager.update_metadata(file_path, metadata):
                self.statusbar.showMessage(f"Updated metadata for: {file_path}")
                self.update_status_statistics()
            else:
                self.statusbar.showMessage("Failed to update metadata")
        except Exception as e:
            logging.error(f"Error handling metadata change: {str(e)}")
            self.show_error_message("Metadata Error", str(e))

    def open_project_folder(self):
        """Open project folder"""
        try:
            folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
            if folder:
                self.file_tree.populate_tree(folder)
                self.statusbar.showMessage(f"Opened folder: {folder}")
        except Exception as e:
            logging.error(f"Error opening project folder: {str(e)}")
            self.show_error_message("Folder Error", str(e))

    def open_metadata_excel(self):
        """Open metadata Excel file"""
        try:
            if os.path.exists(self.metadata_manager.excel_path):
                os.startfile(self.metadata_manager.excel_path)
            else:
                self.show_error_message("Error", "Metadata file not found")
        except Exception as e:
            logging.error(f"Error opening metadata Excel: {str(e)}")
            self.show_error_message("Error", str(e))

    def add_selected_to_database(self):
        """Add currently selected files to database"""
        try:
            selected_files = self.file_tree.get_selected_file_paths()
            if selected_files:
                self.handle_files_added(selected_files)
            else:
                self.statusbar.showMessage("No files selected")
        except Exception as e:
            logging.error(f"Error adding selected files: {str(e)}")
            self.show_error_message("Error", str(e))

    def clear_metadata_cache(self):
        """Clear metadata cache"""
        try:
            self.metadata_manager.clear_cache()
            self.statusbar.showMessage("Metadata cache cleared")
        except Exception as e:
            logging.error(f"Error clearing metadata cache: {str(e)}")
            self.show_error_message("Error", str(e))

    def update_status_statistics(self):
        """Update status bar with current statistics"""
        try:
            stats = self.metadata_manager.get_statistics()
            self.stats_label.setText(
                f"Files in Database: {stats.get('total_files', 0)} | "
                f"Departments: {len(stats.get('departments', []))} | "
                f"File Types: {len(stats.get('file_types', []))}"
            )
        except Exception as e:
            logging.error(f"Error updating statistics: {str(e)}")

    def show_statistics(self):
        """Show detailed statistics dialog"""
        try:
            stats = self.metadata_manager.get_statistics()
            QMessageBox.information(self, "Database Statistics",
                f"Total Files: {stats.get('total_files', 0)}\n"
                f"Departments: {', '.join(stats.get('departments', []))}\n"
                f"File Types: {', '.join(stats.get('file_types', []))}\n"
                f"Newest File: {stats.get('newest_file', 'N/A')}\n"
                f"Oldest File: {stats.get('oldest_file', 'N/A')}"
            )
        except Exception as e:
            logging.error(f"Error showing statistics: {str(e)}")
            self.show_error_message("Error", str(e))

    def refresh_view(self):
        """Refresh the current view"""
        try:
            self.statusbar.showMessage("Refreshing view...")
            current_path = self.config.get_network_paths()['root']
            self.file_tree.populate_tree(current_path)
            self.metadata_manager.clear_cache()
            self.update_status_statistics()
            self.statusbar.showMessage("View refreshed")
        except Exception as e:
            logging.error(f"Error refreshing view: {str(e)}")
            self.show_error_message("Refresh Error", str(e))

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About", 
                         "Project File Navigator\nVersion 1.0\n\n"
                         "A file management system with metadata support.\n\n"
                         "Features:\n"
                         "- File browsing\n"
                         "- Metadata management\n"
                         "- Search and filtering\n"
                         "- Excel integration")

    def show_error_message(self, title, message):
        """Show error message dialog"""
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        """Handle application close"""
        try:
            # Save window state
            self.config.update_setting('ui', {
                'window_size': [self.width(), self.height()],
                'splitter_sizes': self.splitter.sizes()
            })
            
            # Save any pending metadata changes
            try:
                self.metadata_manager.save_database()
            except Exception as save_error:
                logging.error(f"Error saving metadata during close: {str(save_error)}")
            
            # Clear caches
            try:
                self.metadata_manager.clear_cache()
            except Exception as cache_error:
                logging.error(f"Error clearing cache during close: {str(cache_error)}")
            
            # Accept the close event
            event.accept()
            
        except Exception as e:
            logging.error(f"Error during close: {str(e)}")
            # Still accept the close event even if there was an error
            event.accept()

    def load_window_state(self):
        """Load saved window state from config"""
        try:
            ui_settings = self.config.get_ui_settings()
            if ui_settings:
                # Restore window size
                size = ui_settings.get('window_size', [1200, 800])
                self.resize(size[0], size[1])
                
                # Restore splitter positions
                splitter_sizes = ui_settings.get('splitter_sizes')
                if splitter_sizes:
                    self.splitter.setSizes(splitter_sizes)
                    
        except Exception as e:
            logging.error(f"Error loading window state: {str(e)}")
            # Use default size if loading fails
            self.resize(1200, 800)

    def show_busy_indicator(self, show: bool = True):
        """Show/hide busy cursor"""
        if show:
            self.setCursor(Qt.CursorShape.WaitCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def check_metadata_changes(self) -> bool:
        """Check if there are unsaved metadata changes"""
        try:
            # Implementation depends on how you track changes
            return self.metadata_editor.has_unsaved_changes()
        except Exception as e:
            logging.error(f"Error checking metadata changes: {str(e)}")
            return False

    def save_all_changes(self) -> bool:
        """Save all pending changes"""
        try:
            return self.metadata_manager.save_database()
        except Exception as e:
            logging.error(f"Error saving all changes: {str(e)}")
            return False