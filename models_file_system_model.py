from PyQt6.QtCore import QAbstractItemModel, Qt, QModelIndex
import os
from datetime import datetime
from typing import List, Dict

class FileSystemModel(QAbstractItemModel):
    def __init__(self):
        super().__init__()
        self.root_path = ""
        self.files_data = []
        self.headers = ["Name", "Type", "Modified", "Size", "Status"]
        
    def setup_model(self, root_path: str):
        """Initialize model with root path"""
        self.root_path = root_path
        self.refresh()

    def refresh(self):
        """Reload file system data"""
        self.beginResetModel()
        self.files_data = self.scan_directory(self.root_path)
        self.endResetModel()

    def scan_directory(self, path: str) -> List[Dict]:
        """Recursively scan directory for files"""
        files = []
        for entry in os.scandir(path):
            file_info = {
                'name': entry.name,
                'path': entry.path,
                'is_dir': entry.is_dir(),
                'size': entry.stat().st_size if entry.is_file() else 0,
                'modified': datetime.fromtimestamp(entry.stat().st_mtime),
                'type': self.get_file_type(entry.name) if entry.is_file() else 'Folder',
                'status': self.get_file_status(entry.path)
            }
            files.append(file_info)
            
            if entry.is_dir():
                files.extend(self.scan_directory(entry.path))
        return files

    def get_file_type(self, filename: str) -> str:
        """Determine file type from extension"""
        ext = os.path.splitext(filename)[1].lower()
        types = {
            '.dwg': 'AutoCAD Drawing',
            '.pdf': 'PDF Document',
            '.doc': 'Word Document',
            '.docx': 'Word Document',
            '.xls': 'Excel Spreadsheet',
            '.xlsx': 'Excel Spreadsheet',
            '.rvt': 'Revit File',
        }
        return types.get(ext, ext[1:] if ext else 'Unknown')

    def get_file_status(self, file_path: str) -> str:
        """Get file status from metadata"""
        # Implement metadata lookup
        return "Unknown"

    def filter_files(self, filters: Dict) -> None:
        """Apply filters to file list"""
        self.beginResetModel()
        filtered_data = self.files_data.copy()
        
        for key, value in filters.items():
            if value and value != "All":
                filtered_data = [f for f in filtered_data 
                               if str(f.get(key)).lower() == value.lower()]
        
        self.files_data = filtered_data
        self.endResetModel()

    def sort_files(self, column: int, order: Qt.SortOrder) -> None:
        """Sort file list by column"""
        self.beginResetModel()
        key = self.headers[column].lower()
        reverse = order == Qt.SortOrder.DescendingOrder
        self.files_data.sort(key=lambda x: x.get(key, ''), reverse=reverse)
        self.endResetModel()

    # Required QAbstractItemModel implementations
    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index: QModelIndex) -> QModelIndex:
        return QModelIndex()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self.files_data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            file = self.files_data[index.row()]
            column = self.headers[index.column()].lower()
            return str(file.get(column, ''))

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, 
                  role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers[section]
        return None

