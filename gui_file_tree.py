from PyQt6.QtWidgets import QTreeView, QMenu, QStyle, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QColor, QFont
import os
import logging
from datetime import datetime

class FileTreeView(QTreeView):
    fileSelected = pyqtSignal(str)
    filesAdded = pyqtSignal(list)  # Signal for bulk file adding
    
    def __init__(self, safety_manager, parent=None):
        super().__init__(parent)
        self.safety = safety_manager
        self.setup_model()
        self.setup_ui()
        self.connect_signals()

    def setup_model(self):
        """Initialize tree model"""
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name', 'Type', 'Modified', 'Size', 'Status'])
        self.setModel(self.model)
        
    def setup_ui(self):
        """Configure tree view appearance"""
        self.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)  # Enable multi-select
        self.setSortingEnabled(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setExpandsOnDoubleClick(False)
        
        # Configure columns
        self.header().setStretchLastSection(False)
        self.header().resizeSection(0, 300)  # Name column
        self.header().resizeSection(1, 100)  # Type column
        self.header().resizeSection(2, 150)  # Modified column
        self.header().resizeSection(3, 80)   # Size column
        self.header().resizeSection(4, 100)  # Status column

    def connect_signals(self):
        """Connect signal handlers"""
        self.doubleClicked.connect(self.handle_double_click)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def populate_tree(self, root_path):
        """Populate tree with files from root path"""
        try:
            self.model.clear()
            self.model.setHorizontalHeaderLabels(['Name', 'Type', 'Modified', 'Size', 'Status'])
            root_item = self.model.invisibleRootItem()
            self._add_tree_items(root_path, root_item)
        except Exception as e:
            logging.error(f"Error populating tree: {str(e)}")

    def _add_tree_items(self, path, parent_item):
        """Recursively add items to tree with read-only indication"""
        try:
            for item in os.scandir(path):
                if not self.safety.safe_read_operation(item.path):
                    continue

                tree_item = QStandardItem(item.name)
                tree_item.setData(item.path, Qt.ItemDataRole.UserRole)
                
                # Set read-only visual indicators
                if self.safety.is_protected_path(item.path):
                    font = tree_item.font()
                    font.setItalic(True)
                    tree_item.setFont(font)
                    tree_item.setForeground(QColor(128, 128, 128))
                    status_text = "Read Only"
                else:
                    status_text = "Writable"

                # Add file metadata
                if item.is_file():
                    size_item = QStandardItem(self._format_size(item.stat().st_size))
                    type_item = QStandardItem(os.path.splitext(item.name)[1])
                    modified_item = QStandardItem(self._format_date(item.stat().st_mtime))
                else:
                    size_item = QStandardItem("")
                    type_item = QStandardItem("Folder")
                    modified_item = QStandardItem("")

                status_item = QStandardItem(status_text)
                
                row = [tree_item, type_item, modified_item, size_item, status_item]
                parent_item.appendRow(row)
                
                if item.is_dir():
                    self._add_tree_items(item.path, tree_item)

        except Exception as e:
            logging.error(f"Error adding tree items for {path}: {str(e)}")

    def handle_double_click(self, index):
        """Handle item double-click"""
        try:
            item = self.model.itemFromIndex(index)
            if item:
                file_path = item.data(Qt.ItemDataRole.UserRole)
                if os.path.isfile(file_path) and self.safety.safe_read_operation(file_path):
                    self.fileSelected.emit(file_path)
        except Exception as e:
            logging.error(f"Error handling double click: {str(e)}")

    def get_selected_file_paths(self):
        """Get paths of all selected files"""
        try:
            paths = []
            for index in self.selectedIndexes():
                if index.column() == 0:  # Only process first column to avoid duplicates
                    item = self.model.itemFromIndex(index)
                    file_path = item.data(Qt.ItemDataRole.UserRole)
                    if os.path.isfile(file_path):  # Only include files, not directories
                        paths.append(file_path)
            return list(set(paths))  # Remove any duplicates
        except Exception as e:
            logging.error(f"Error getting selected file paths: {str(e)}")
            return []

    def show_context_menu(self, position):
        """Show right-click context menu"""
        try:
            indexes = self.selectedIndexes()
            if not indexes:
                return

            menu = QMenu()
            
            # Get selected file paths
            selected_paths = self.get_selected_file_paths()
            
            if len(selected_paths) > 0:
                # Add metadata option for multiple files
                menu.addAction("Add Files to Database", lambda: self.add_files_to_database(selected_paths))
                menu.addSeparator()
            
            if len(selected_paths) == 1:
                # Single file options
                file_path = selected_paths[0]
                if not self.safety.is_protected_path(file_path):
                    menu.addAction("Open", lambda: self.handle_double_click(indexes[0]))
                menu.addAction("Show in Explorer", lambda: self._show_in_explorer(file_path))
                menu.addAction("Properties", lambda: self._show_properties(file_path))
            
            menu.exec(self.viewport().mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"Error showing context menu: {str(e)}")

    def add_files_to_database(self, file_paths):
        """Add selected files to metadata database"""
        try:
            # Emit signal with list of files to be added
            self.filesAdded.emit(file_paths)
            
            # Show confirmation
            count = len(file_paths)
            QMessageBox.information(self, "Success", 
                                  f"Added {count} file{'s' if count != 1 else ''} to database.")
        except Exception as e:
            logging.error(f"Error adding files to database: {str(e)}")
            QMessageBox.critical(self, "Error", 
                               f"Failed to add files to database: {str(e)}")

    def _show_in_explorer(self, path):
        """Show file in explorer"""
        try:
            if os.path.exists(path):
                os.startfile(os.path.dirname(path))
        except Exception as e:
            logging.error(f"Error showing in explorer: {str(e)}")

    def _show_properties(self, path):
        """Show file properties"""
        try:
            if hasattr(self.parent(), 'show_properties_dialog'):
                self.parent().show_properties_dialog(path)
        except Exception as e:
            logging.error(f"Error showing properties: {str(e)}")

    @staticmethod
    def _format_size(size):
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def _format_date(timestamp):
        """Format date for display"""
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')