
from typing import List, Set
import os
import logging
from pathlib import Path

class AccessSafety:
    def __init__(self):
        self.read_only_paths: Set[str] = set()
        self.setup_logging()
        
    def setup_logging(self):
        """Configure safety logging"""
        logging.basicConfig(
            filename='access_safety.log',
            level=logging.WARNING,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def set_protected_paths(self, paths: List[str]):
        """Set paths that should be read-only"""
        self.read_only_paths = {os.path.normpath(p) for p in paths}
    
    def is_protected_path(self, path: str) -> bool:
        """Check if path is in protected area"""
        normalized_path = os.path.normpath(path)
        return any(normalized_path.startswith(protected) 
                  for protected in self.read_only_paths)
    
    def validate_operation(self, path: str, operation_type: str) -> bool:
        """
        Validate if operation is allowed
        operation_type: 'read' or 'write'
        """
        if operation_type.lower() == 'write' and self.is_protected_path(path):
            logging.warning(f"Blocked write attempt to protected path: {path}")
            return False
        return True
    
    def safe_read_operation(self, path: str) -> bool:
        """Validate read operation"""
        try:
            return os.access(path, os.R_OK)
        except Exception as e:
            logging.error(f"Read validation error: {str(e)}")
            return False
    
    @staticmethod
    def is_modification_operation(operation: str) -> bool:
        """Determine if operation could modify files"""
        modify_operations = {
            'write', 'delete', 'move', 'rename', 'create',
            'modify', 'update', 'save', 'edit'
        }
        return operation.lower() in modify_operations