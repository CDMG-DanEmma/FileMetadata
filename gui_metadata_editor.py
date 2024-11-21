from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
                            QComboBox, QTextEdit, QPushButton, QScrollArea,
                            QLabel, QGroupBox, QMessageBox, QFrame)
from PyQt6.QtCore import pyqtSignal
import logging
from datetime import datetime
import os

class MetadataEditor(QWidget):
    metadataChanged = pyqtSignal(str, dict)  # file_path, metadata
    
    def __init__(self, safety_manager, parent=None):
        super().__init__(parent)
        self.safety = safety_manager
        self.current_file = None
        self.has_changes = False
        try:
            self.setup_ui()
            self.setup_fields()
            self.connect_signals()
        except Exception as e:
            logging.error(f"Error initializing MetadataEditor: {str(e)}")
            raise

    def setup_ui(self):
        """Initialize metadata editor UI"""
        try:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create title section
            self.title_section = QFrame()
            title_layout = QVBoxLayout(self.title_section)
            self.title_label = QLabel("No File Selected")
            self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.path_label = QLabel("")
            self.path_label.setStyleSheet("color: #888888; font-size: 11px;")
            title_layout.addWidget(self.title_label)
            title_layout.addWidget(self.path_label)
            main_layout.addWidget(self.title_section)
            
            # Create scroll area
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            content_widget = QWidget()
            self.scroll_layout = QVBoxLayout(content_widget)
            self.scroll_layout.setContentsMargins(0, 0, 0, 0)
            scroll.setWidget(content_widget)
            main_layout.addWidget(scroll)
            
            # Add save button
            self.save_button = QPushButton("Save Metadata")
            self.save_button.clicked.connect(self.save_metadata)
            self.save_button.setEnabled(False)
            main_layout.addWidget(self.save_button)
            
        except Exception as e:
            logging.error(f"Error in setup_ui: {str(e)}")
            raise

    def setup_fields(self):
        """Create metadata input fields"""
        try:
            # File Information (Read-only)
            file_group = QGroupBox("File Information")
            file_layout = QFormLayout()
            
            self.file_name = QLineEdit()
            self.file_name.setReadOnly(True)
            self.file_size = QLineEdit()
            self.file_size.setReadOnly(True)
            self.file_type = QLineEdit()
            self.file_type.setReadOnly(True)
            self.date_added = QLineEdit()
            self.date_added.setReadOnly(True)
            self.last_modified = QLineEdit()
            self.last_modified.setReadOnly(True)
            
            file_layout.addRow("File Name:", self.file_name)
            file_layout.addRow("Size:", self.file_size)
            file_layout.addRow("Type:", self.file_type)
            file_layout.addRow("Date Added:", self.date_added)
            file_layout.addRow("Last Modified:", self.last_modified)
            file_group.setLayout(file_layout)
            self.scroll_layout.addWidget(file_group)

            # Project Information
            project_group = QGroupBox("Project Information")
            project_layout = QFormLayout()
            
            self.project_number = QLineEdit()
            self.department = QComboBox()
            self.department.addItems(["", "Electrical", "Civil", "Facility Planning", 
                                    "Piping", "Mechanical", "Automation", "Project Management"])
            self.area = QComboBox()
            self.area.addItems(["", "Furnace/Melting", "Lehr/Cooling", "Batch House", 
                              "Forming", "Cold End", "Quality Control Lab"])
            
            project_layout.addRow("Project Number:", self.project_number)
            project_layout.addRow("Department:", self.department)
            project_layout.addRow("Area:", self.area)
            project_group.setLayout(project_layout)
            self.scroll_layout.addWidget(project_group)

            # Document Properties
            doc_group = QGroupBox("Document Properties")
            doc_layout = QFormLayout()
            
            self.doc_type = QComboBox()
            self.doc_type.addItems(["", "Plan View", "Single Line Diagram", "Elevation View", 
                                  "Section View", "Equipment Layout"])
            self.source = QComboBox()
            self.source.addItems(["", "Internal (CDMG)", "Vendor", "Client"])
            self.revision = QLineEdit()
            self.status = QComboBox()
            self.status.addItems(["", "For Review", "For Bid", "For Construction", "As-Built"])
            self.work_status = QComboBox()
            self.work_status.addItems(["", "Not Started", "In Progress", "On Hold", "Complete"])
            
            doc_layout.addRow("Type:", self.doc_type)
            doc_layout.addRow("Source:", self.source)
            doc_layout.addRow("Revision:", self.revision)
            doc_layout.addRow("Issue Status:", self.status)
            doc_layout.addRow("Work Status:", self.work_status)
            doc_group.setLayout(doc_layout)
            self.scroll_layout.addWidget(doc_group)

            # Technical Reference
            tech_group = QGroupBox("Technical Reference")
            tech_layout = QFormLayout()
            
            self.codes = QLineEdit()
            self.equipment = QLineEdit()
            self.related_docs = QLineEdit()
            
            tech_layout.addRow("Applicable Codes:", self.codes)
            tech_layout.addRow("Equipment Tags:", self.equipment)
            tech_layout.addRow("Related Documents:", self.related_docs)
            tech_group.setLayout(tech_layout)
            self.scroll_layout.addWidget(tech_group)

            # Comments
            comments_group = QGroupBox("Comments")
            comments_layout = QVBoxLayout()
            self.comments = QTextEdit()
            self.comments.setMaximumHeight(100)
            comments_layout.addWidget(self.comments)
            comments_group.setLayout(comments_layout)
            self.scroll_layout.addWidget(comments_group)

            # Add spacer at the bottom
            self.scroll_layout.addStretch()

        except Exception as e:
            logging.error(f"Error in setup_fields: {str(e)}")
            raise

    def connect_signals(self):
        """Connect signal handlers"""
        try:
            # Connect change signals to enable save button
            for widget in [self.project_number, self.revision, self.codes, 
                         self.equipment, self.related_docs]:
                widget.textChanged.connect(self.handle_field_change)
            
            for widget in [self.department, self.area, self.doc_type, 
                         self.source, self.status, self.work_status]:
                widget.currentTextChanged.connect(self.handle_field_change)
            
            self.comments.textChanged.connect(self.handle_field_change)
            
        except Exception as e:
            logging.error(f"Error connecting signals: {str(e)}")
            raise

    def handle_field_change(self):
        """Handle changes to any field"""
        if self.current_file:
            self.has_changes = True
            self.save_button.setEnabled(True)

    def load_file_metadata(self, file_path: str, metadata: dict = None):
        """Load metadata for selected file"""
        try:
            self.current_file = file_path
            self.has_changes = False
            self.title_label.setText(f"Metadata: {os.path.basename(file_path)}")
            self.path_label.setText(file_path)
            
            # Check if file is in protected path
            if self.safety.is_protected_path(file_path):
                self.set_read_only_mode(True)
            else:
                self.set_read_only_mode(False)
            
            if metadata:
                self.populate_fields(metadata)
            else:
                self.clear_fields()
                # Populate basic file information
                self.populate_file_info(file_path)
                
        except Exception as e:
            logging.error(f"Error loading metadata for {file_path}: {str(e)}")
            self.show_error_message("Error", f"Failed to load metadata: {str(e)}")

    def populate_file_info(self, file_path: str):
        """Populate basic file information"""
        try:
            stats = os.stat(file_path)
            self.file_name.setText(os.path.basename(file_path))
            self.file_size.setText(self.format_size(stats.st_size))
            self.file_type.setText(os.path.splitext(file_path)[1])
            self.date_added.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            self.last_modified.setText(
                datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            )
        except Exception as e:
            logging.error(f"Error populating file info: {str(e)}")

    def populate_fields(self, metadata: dict):
        """Fill form fields with metadata"""
        try:
            # File information
            self.file_name.setText(metadata.get('file_name', ''))
            self.file_size.setText(metadata.get('file_size', ''))
            self.file_type.setText(metadata.get('file_extension', ''))
            self.date_added.setText(str(metadata.get('date_added', '')))
            self.last_modified.setText(str(metadata.get('last_modified', '')))
            
            # Project information
            self.project_number.setText(metadata.get('project_number', ''))
            self.department.setCurrentText(metadata.get('department', ''))
            self.area.setCurrentText(metadata.get('area', ''))
            
            # Document properties
            self.doc_type.setCurrentText(metadata.get('type', ''))
            self.source.setCurrentText(metadata.get('source', ''))
            self.revision.setText(metadata.get('revision', ''))
            self.status.setCurrentText(metadata.get('issue_status', ''))
            self.work_status.setCurrentText(metadata.get('work_status', ''))
            
            # Technical reference
            self.codes.setText(metadata.get('applicable_codes', ''))
            self.equipment.setText(metadata.get('equipment_tags', ''))
            self.related_docs.setText(metadata.get('related_documents', ''))
            
            # Comments
            self.comments.setText(metadata.get('comments', ''))
            
            self.save_button.setEnabled(False)
            self.has_changes = False
            
        except Exception as e:
            logging.error(f"Error populating fields: {str(e)}")
            raise

    def clear_fields(self):
        """Clear all form fields"""
        try:
            # Clear file information
            self.file_name.clear()
            self.file_size.clear()
            self.file_type.clear()
            self.date_added.clear()
            self.last_modified.clear()
            
            # Clear project information
            self.project_number.clear()
            self.department.setCurrentIndex(0)
            self.area.setCurrentIndex(0)
            
            # Clear document properties
            self.doc_type.setCurrentIndex(0)
            self.source.setCurrentIndex(0)
            self.revision.clear()
            self.status.setCurrentIndex(0)
            self.work_status.setCurrentIndex(0)
            
            # Clear technical reference
            self.codes.clear()
            self.equipment.clear()
            self.related_docs.clear()
            
            # Clear comments
            self.comments.clear()
            
            self.save_button.setEnabled(False)
            self.has_changes = False
            
        except Exception as e:
            logging.error(f"Error clearing fields: {str(e)}")
            raise

    def set_read_only_mode(self, read_only: bool):
        """Set read-only mode for all fields"""
        try:
            for widget in [self.project_number, self.revision, self.codes,
                         self.equipment, self.related_docs, self.comments]:
                if isinstance(widget, QLineEdit):
                    widget.setReadOnly(read_only)
                elif isinstance(widget, QTextEdit):
                    widget.setReadOnly(read_only)
            
            for widget in [self.department, self.area, self.doc_type,
                         self.source, self.status, self.work_status]:
                widget.setEnabled(not read_only)
            
            self.save_button.setEnabled(not read_only and self.has_changes)
            
        except Exception as e:
            logging.error(f"Error setting read-only mode: {str(e)}")
            raise

    def save_metadata(self):
        """Save current metadata"""
        if not self.current_file:
            return
            
        try:
            metadata = {
                'file_path': self.current_file,
                'file_name': self.file_name.text(),
                'file_location': os.path.dirname(self.current_file),
                'file_extension': self.file_type.text(),
                'file_size': self.file_size.text(),
                'date_added': self.date_added.text(),
                'last_modified': datetime.now(),
                
                'project_number': self.project_number.text(),
                'department': self.department.currentText(),
                'area': self.area.currentText(),
                
                'type': self.doc_type.currentText(),
                'source': self.source.currentText(),
                'revision': self.revision.text(),
                'issue_status': self.status.currentText(),
                'work_status': self.work_status.currentText(),
                
                'applicable_codes': self.codes.text(),
                'equipment_tags': self.equipment.text(),
                'related_documents': self.related_docs.text(),
                
                'comments': self.comments.toPlainText()
            }
            
            self.metadataChanged.emit(self.current_file, metadata)
            self.save_button.setEnabled(False)
            self.has_changes = False
            
        except Exception as e:
            logging.error(f"Error saving metadata: {str(e)}")
            self.show_error_message("Error", f"Failed to save metadata: {str(e)}")

    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        return self.has_changes

    def show_error_message(self, title: str, message: str):
        """Show error message dialog"""
        QMessageBox.critical(self, title, message)

    @staticmethod
    def format_size(size: int) -> str:
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        # Adjust scroll area if needed
        self.adjustScrollArea()

    def adjustScrollArea(self):
        """Adjust scroll area dimensions"""
        try:
            # Ensure proper scroll area sizing
            scroll_widget = self.findChild(QScrollArea)
            if scroll_widget:
                available_height = self.height() - self.title_section.height() - self.save_button.height() - 20
                scroll_widget.setMinimumHeight(available_height)
        except Exception as e:
            logging.error(f"Error adjusting scroll area: {str(e)}")

    def showEvent(self, event):
        """Handle show events"""
        super().showEvent(event)
        self.adjustScrollArea()
        
    def keyPressEvent(self, event):
        """Handle key press events"""
        try:
            # Ctrl+S to save
            if event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_S:
                if self.save_button.isEnabled():
                    self.save_metadata()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            logging.error(f"Error handling key press: {str(e)}")
            super().keyPressEvent(event)
            
    def validate_input(self) -> bool:
        """Validate input fields"""
        try:
            # Add any validation rules here
            return True
        except Exception as e:
            logging.error(f"Error validating input: {str(e)}")
            return False

    def reset_changes(self):
        """Reset changes since last save"""
        try:
            if self.current_file:
                self.load_file_metadata(self.current_file)
        except Exception as e:
            logging.error(f"Error resetting changes: {str(e)}")
            
    def update_file_info(self):
        """Update file information display"""
        try:
            if self.current_file and os.path.exists(self.current_file):
                self.populate_file_info(self.current_file)
        except Exception as e:
            logging.error(f"Error updating file info: {str(e)}")

    def get_current_metadata(self) -> dict:
        """Get current metadata values"""
        try:
            if not self.current_file:
                return {}
                
            return {
                'file_path': self.current_file,
                'file_name': self.file_name.text(),
                'file_location': os.path.dirname(self.current_file),
                'file_extension': self.file_type.text(),
                'file_size': self.file_size.text(),
                'date_added': self.date_added.text(),
                'last_modified': datetime.now(),
                
                'project_number': self.project_number.text(),
                'department': self.department.currentText(),
                'area': self.area.currentText(),
                
                'type': self.doc_type.currentText(),
                'source': self.source.currentText(),
                'revision': self.revision.text(),
                'issue_status': self.status.currentText(),
                'work_status': self.work_status.currentText(),
                
                'applicable_codes': self.codes.text(),
                'equipment_tags': self.equipment.text(),
                'related_documents': self.related_docs.text(),
                
                'comments': self.comments.toPlainText()
            }
        except Exception as e:
            logging.error(f"Error getting current metadata: {str(e)}")
            return {}

    def closeEvent(self, event):
        """Handle editor close event"""
        try:
            if self.has_unsaved_changes():
                reply = QMessageBox.question(
                    self, "Unsaved Changes",
                    "You have unsaved changes. Do you want to save them?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                
                if reply == QMessageBox.Save:
                    self.save_metadata()
                    event.accept()
                elif reply == QMessageBox.Discard:
                    event.accept()
                else:
                    event.ignore()
            else:
                event.accept()
        except Exception as e:
            logging.error(f"Error handling close event: {str(e)}")
            event.accept()