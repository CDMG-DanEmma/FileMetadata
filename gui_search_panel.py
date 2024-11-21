from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                            QComboBox, QPushButton, QLabel, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt
import logging

class SearchPanel(QWidget):
    searchRequested = pyqtSignal(str)
    filterChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
        self.load_initial_filters()

    def setup_ui(self):
        """Initialize search panel UI"""
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(6, 6, 6, 6)
            layout.setSpacing(8)
            
            # Search bar layout
            search_layout = QHBoxLayout()
            
            # Search input with placeholder
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("Search files...")
            self.search_input.setMinimumHeight(28)
            self.search_input.setClearButtonEnabled(True)  # Add clear button
            
            # Search button
            self.search_button = QPushButton("Search")
            self.search_button.setMinimumHeight(28)
            self.search_button.setDefault(True)  # Make it the default button
            
            search_layout.addWidget(self.search_input)
            search_layout.addWidget(self.search_button)
            
            # Filters layout
            filter_layout = QHBoxLayout()
            filter_layout.setSpacing(12)
            
            # File type filter
            type_layout = QHBoxLayout()
            type_label = QLabel("Type:")
            type_label.setMinimumWidth(40)
            self.type_filter = QComboBox()
            self.type_filter.addItems([
                "All Types",
                "Plan View",
                "Single Line Diagram",
                "Elevation View",
                "Section View",
                "Equipment Layout",
                "Cable Tray Layout",
                "Conduit Layout",
                "Piping Layout",
                "Foundation Plan",
                "Structural Details"
            ])
            type_layout.addWidget(type_label)
            type_layout.addWidget(self.type_filter)
            
            # Department filter
            dept_layout = QHBoxLayout()
            dept_label = QLabel("Department:")
            dept_label.setMinimumWidth(80)
            self.dept_filter = QComboBox()
            self.dept_filter.addItems([
                "All Departments",
                "Electrical",
                "Civil",
                "Facility Planning",
                "Piping",
                "Mechanical",
                "Automation",
                "Project Management"
            ])
            dept_layout.addWidget(dept_label)
            dept_layout.addWidget(self.dept_filter)
            
            # Status filter
            status_layout = QHBoxLayout()
            status_label = QLabel("Status:")
            status_label.setMinimumWidth(50)
            self.status_filter = QComboBox()
            self.status_filter.addItems([
                "All Status",
                "For Review",
                "For Bid",
                "For Construction",
                "As-Built",
                "Not Started",
                "In Progress",
                "On Hold",
                "Complete"
            ])
            status_layout.addWidget(status_label)
            status_layout.addWidget(self.status_filter)
            
            # Add filter layouts to main filter layout
            filter_layout.addLayout(type_layout)
            filter_layout.addLayout(dept_layout)
            filter_layout.addLayout(status_layout)
            
            # Reset filters button
            self.reset_button = QPushButton("Reset")
            self.reset_button.setMaximumWidth(60)
            filter_layout.addWidget(self.reset_button)
            
            # Add separator line
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setFrameShadow(QFrame.Shadow.Sunken)
            
            # Add layouts to main layout
            layout.addLayout(search_layout)
            layout.addLayout(filter_layout)
            layout.addWidget(line)

            self.setMaximumHeight(100)
            
        except Exception as e:
            logging.error(f"Error setting up search panel UI: {str(e)}")
            raise

    def connect_signals(self):
        """Connect signal handlers"""
        try:
            # Search signals
            self.search_button.clicked.connect(self.execute_search)
            self.search_input.returnPressed.connect(self.execute_search)
            
            # Filter signals
            self.type_filter.currentTextChanged.connect(self.handle_filter_change)
            self.dept_filter.currentTextChanged.connect(self.handle_filter_change)
            self.status_filter.currentTextChanged.connect(self.handle_filter_change)
            
            # Reset button
            self.reset_button.clicked.connect(self.reset_filters)
            
        except Exception as e:
            logging.error(f"Error connecting search panel signals: {str(e)}")
            raise

    def load_initial_filters(self):
        """Load initial filter values"""
        try:
            # Could load from config or leave as default
            self.reset_filters()
        except Exception as e:
            logging.error(f"Error loading initial filters: {str(e)}")

    def execute_search(self):
        """Execute search with current text and filters"""
        try:
            search_text = self.search_input.text().strip()
            if search_text:
                self.searchRequested.emit(search_text)
                self.handle_filter_change()  # Also apply current filters
        except Exception as e:
            logging.error(f"Error executing search: {str(e)}")

    def handle_filter_change(self):
        """Handle changes to any filter"""
        try:
            filters = {
                'type': self.type_filter.currentText(),
                'department': self.dept_filter.currentText(),
                'status': self.status_filter.currentText()
            }
            self.filterChanged.emit(filters)
        except Exception as e:
            logging.error(f"Error handling filter change: {str(e)}")

    def reset_filters(self):
        """Reset all filters to default values"""
        try:
            self.search_input.clear()
            self.type_filter.setCurrentText("All Types")
            self.dept_filter.setCurrentText("All Departments")
            self.status_filter.setCurrentText("All Status")
            
            # Emit filter change event with reset values
            self.handle_filter_change()
        except Exception as e:
            logging.error(f"Error resetting filters: {str(e)}")

    def get_current_filters(self):
        """Return current filter settings"""
        return {
            'search_text': self.search_input.text().strip(),
            'type': self.type_filter.currentText(),
            'department': self.dept_filter.currentText(),
            'status': self.status_filter.currentText()
        }

    def set_filters(self, filters):
        """Set filters from a dictionary"""
        try:
            if 'search_text' in filters:
                self.search_input.setText(filters['search_text'])
            if 'type' in filters:
                self.type_filter.setCurrentText(filters['type'])
            if 'department' in filters:
                self.dept_filter.setCurrentText(filters['department'])
            if 'status' in filters:
                self.status_filter.setCurrentText(filters['status'])
            
            self.handle_filter_change()
        except Exception as e:
            logging.error(f"Error setting filters: {str(e)}")

    def keyPressEvent(self, event):
        """Handle key press events"""
        try:
            if event.key() == Qt.Key.Key_Escape:
                self.search_input.clear()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            logging.error(f"Error handling key press: {str(e)}")