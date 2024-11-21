
from PyQt6.QtWidgets import QMenu
from PyQt6.QtCore import Qt
import os

class FileContextMenu:
    def __init__(self, parent=None):
        self.parent = parent
        self.menu = None

    def create_menu(self, selected_files):
        """Create context menu for selected files"""
        self.menu = QMenu(self.parent)
        self.selected_files = selected_files

        # File operations
        self.menu.addAction("Open", self.open_file)
        self.menu.addAction("Open Containing Folder", self.open_folder)
        self.menu.addSeparator()
        
        # Metadata operations
        self.menu.addAction("Edit Metadata", self.edit_metadata)
        self.menu.addAction("Copy File Path", self.copy_path)
        self.menu.addSeparator()
        
        # File information
        self.menu.addAction("Properties", self.show_properties)
        
        return self.menu

    def open_file(self):
        """Open selected file with default application"""
        for file_path in self.selected_files:
            if os.path.exists(file_path):
                os.startfile(file_path)

    def open_folder(self):
        """Open containing folder in explorer"""
        for file_path in self.selected_files:
            folder = os.path.dirname(file_path)
            if os.path.exists(folder):
                os.startfile(folder)

    def edit_metadata(self):
        """Open metadata editor for selected file"""
        if self.parent and hasattr(self.parent, 'show_metadata_editor'):
            self.parent.show_metadata_editor(self.selected_files[0])

    def copy_path(self):
        """Copy file path to clipboard"""
        if self.selected_files:
            clipboard = self.parent.application().clipboard()
            clipboard.setText(self.selected_files[0])

    def show_properties(self):
        """Show file properties dialog"""
        if self.parent and hasattr(self.parent, 'show_properties_dialog'):
            self.parent.show_properties_dialog(self.selected_files[0])