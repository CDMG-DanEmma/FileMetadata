import os
import subprocess
import logging
from typing import List, Optional, Tuple
from datetime import datetime
from PyQt6.QtCore import QMimeDatabase

class FileOperations:
    def __init__(self, safety_manager):
        self.mime_db = QMimeDatabase()
        self.safety = safety_manager
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for file operations"""
        logging.basicConfig(
            filename='file_operations.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def open_file(self, file_path: str, read_only: bool = True) -> bool:
        """
        Open file with default application in read-only mode
        Returns: Success status
        """
        try:
            if not self.safety.safe_read_operation(file_path):
                logging.warning(f"Access denied to file: {file_path}")
                return False

            if os.name == 'nt':  # Windows
                if read_only:
                    # Use notepad's read-only mode or similar for text files
                    if file_path.lower().endswith(('.txt', '.log', '.csv')):
                        subprocess.Popen(['notepad', '/r', file_path])
                    else:
                        os.startfile(file_path)
                else:
                    os.startfile(file_path)
            else:  # Linux/Mac
                subprocess.call(('xdg-open', file_path))
            
            logging.info(f"Successfully opened file: {file_path}")
            return True

        except Exception as e:
            logging.error(f"Error opening file {file_path}: {str(e)}")
            return False

    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get detailed file information (read-only operation)
        Returns: Dictionary with file details
        """
        try:
            if not self.safety.safe_read_operation(file_path):
                return None

            stats = os.stat(file_path)
            return {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stats.st_size,
                'created': datetime.fromtimestamp(stats.st_ctime),
                'modified': datetime.fromtimestamp(stats.st_mtime),
                'accessed': datetime.fromtimestamp(stats.st_atime),
                'type': self.get_file_type(file_path),
                'extension': os.path.splitext(file_path)[1].lower(),
                'is_hidden': os.path.basename(file_path).startswith('.'),
                'is_readonly': True  # Force read-only flag
            }

        except Exception as e:
            logging.error(f"Error getting file info for {file_path}: {str(e)}")
            return None

    def get_file_type(self, file_path: str) -> str:
        """
        Determine file type using mime database (read-only operation)
        Returns: File type description
        """
        try:
            if not self.safety.safe_read_operation(file_path):
                return "Unknown"

            mime_type = self.mime_db.mimeTypeForFile(file_path)
            return mime_type.comment()
        except:
            ext = os.path.splitext(file_path)[1].lower()
            types = {
                '.dwg': 'AutoCAD Drawing',
                '.pdf': 'PDF Document',
                '.doc': 'Word Document',
                '.docx': 'Word Document',
                '.xls': 'Excel Spreadsheet',
                '.xlsx': 'Excel Spreadsheet',
                '.rvt': 'Revit File',
                '.txt': 'Text File',
                '.csv': 'CSV File',
                '.zip': 'Compressed Archive'
            }
            return types.get(ext, f"{ext[1:].upper()} File" if ext else "Unknown")

    def get_directory_size(self, directory: str) -> Tuple[int, int]:
        """
        Calculate directory size and file count (read-only operation)
        Returns: (total_size, file_count)
        """
        if not self.safety.safe_read_operation(directory):
            return (0, 0)

        total_size = 0
        file_count = 0
        
        try:
            for root, _, files in os.walk(directory):
                if not self.safety.safe_read_operation(root):
                    continue
                    
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.safety.safe_read_operation(file_path):
                        try:
                            total_size += os.path.getsize(file_path)
                            file_count += 1
                        except:
                            continue
            
            return total_size, file_count

        except Exception as e:
            logging.error(f"Error calculating directory size for {directory}: {str(e)}")
            return 0, 0

    def get_recent_files(self, directory: str, days: int = 7) -> List[str]:
        """
        Get list of recently modified files (read-only operation)
        Returns: List of file paths
        """
        if not self.safety.safe_read_operation(directory):
            return []

        recent_files = []
        cutoff_time = datetime.now().timestamp() - (days * 86400)

        try:
            for root, _, files in os.walk(directory):
                if not self.safety.safe_read_operation(root):
                    continue
                    
                for file in files:
                    file_path = os.path.join(root, file)
                    if self.safety.safe_read_operation(file_path):
                        try:
                            mod_time = os.path.getmtime(file_path)
                            if mod_time > cutoff_time:
                                recent_files.append(file_path)
                        except:
                            continue

            return sorted(recent_files, key=lambda x: os.path.getmtime(x), reverse=True)

        except Exception as e:
            logging.error(f"Error getting recent files for {directory}: {str(e)}")
            return []

    def format_file_size(self, size_in_bytes: int) -> str:
        """Format file size for display"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.1f} PB"

    def check_file_access(self, file_path: str) -> dict:
        """
        Check file permissions and access (read-only operation)
        Returns: Dictionary with access rights
        """
        result = {
            'exists': False,
            'readable': False,
            'writable': False,  # Always False for protected paths
            'executable': False,
            'is_protected': False,
            'error': None
        }
        
        try:
            result['exists'] = os.path.exists(file_path)
            result['readable'] = self.safety.safe_read_operation(file_path)
            result['is_protected'] = self.safety.is_protected_path(file_path)
            result['writable'] = False  # Enforce read-only
            result['executable'] = os.access(file_path, os.X_OK) if result['readable'] else False

        except Exception as e:
            result['error'] = str(e)
            logging.error(f"Error checking file access for {file_path}: {str(e)}")

        return result

    def create_file_preview(self, file_path: str, max_size: int = 1024) -> Optional[str]:
        """
        Create a preview of text-based files (read-only operation)
        Returns: File preview text or None
        """
        if not self.safety.safe_read_operation(file_path):
            return None

        try:
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                return None

            # Check if file is text-based
            mime_type = self.mime_db.mimeTypeForFile(file_path)
            if not mime_type.inherits('text/plain'):
                return None

            # Read preview
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(max_size)
                if len(content) == max_size:
                    content += "..."
                return content

        except Exception as e:
            logging.error(f"Error creating preview for {file_path}: {str(e)}")
            return None