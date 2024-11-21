import os
import logging
from typing import List, Dict, Optional
import socket
from pathlib import Path

class PathManager:
    def __init__(self, root_path: str = "P:/"):
        self.root_path = root_path
        self.network_available = False
        self.mapped_drives = {}
        self.setup_logging()
        self.verify_network_access()

    def setup_logging(self):
        """Configure logging for path operations"""
        logging.basicConfig(
            filename='path_operations.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def verify_network_paths(self, paths: Dict[str, str]) -> bool:
        """Verify network paths are accessible"""
        try:
            for key, path in paths.items():
                if not os.path.exists(path):
                    logging.warning(f"Network path not accessible: {path}")
                    return False
            return True
        except Exception as e:
            logging.error(f"Error verifying network paths: {str(e)}")
            return False

    def verify_network_access(self) -> bool:
        """Verify network and drive accessibility"""
        try:
            # Check network connectivity
            socket.gethostbyname(socket.gethostname())
            
            # Check if root path exists and is accessible
            if os.path.exists(self.root_path):
                self.network_available = True
                logging.info(f"Network access verified. Root path: {self.root_path}")
                return True
            else:
                self.network_available = False
                logging.error(f"Root path not accessible: {self.root_path}")
                return False

        except Exception as e:
            self.network_available = False
            logging.error(f"Network verification failed: {str(e)}")
            return False
    

    def get_mapped_drives(self) -> Dict[str, str]:
        """Get dictionary of mapped network drives"""
        drives = {}
        try:
            if os.name == 'nt':  # Windows
                import win32wnet
                for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    try:
                        drive = f"{letter}:"
                        win32wnet.WNetGetConnection(drive)
                        drives[drive] = os.path.realpath(drive)
                    except:
                        continue
            else:  # Linux/Mac
                # Implement equivalent for other OS
                pass

            self.mapped_drives = drives
            return drives

        except Exception as e:
            logging.error(f"Error getting mapped drives: {str(e)}")
            return {}

    def normalize_path(self, path: str) -> str:
        """Normalize path format for consistency"""
        try:
            # Convert to absolute path
            if not os.path.isabs(path):
                path = os.path.join(self.root_path, path)
            
            # Normalize separators and case
            normalized = os.path.normpath(path)
            
            # Convert to network path format if applicable
            if os.name == 'nt':
                normalized = normalized.replace('\\', '/')
            
            return normalized

        except Exception as e:
            logging.error(f"Error normalizing path {path}: {str(e)}")
            return path

    def get_relative_path(self, path: str) -> str:
        """Get path relative to root directory"""
        try:
            absolute_path = self.normalize_path(path)
            return os.path.relpath(absolute_path, self.root_path)
        except Exception as e:
            logging.error(f"Error getting relative path for {path}: {str(e)}")
            return path

    def resolve_path(self, path: str) -> Optional[str]:
        """Resolve network path to absolute path"""
        try:
            # Check if path exists
            if not self.verify_path(path):
                return None
                
            # Resolve any symbolic links
            resolved = os.path.realpath(path)
            
            # Normalize the resolved path
            normalized = self.normalize_path(resolved)
            
            return normalized

        except Exception as e:
            logging.error(f"Error resolving path {path}: {str(e)}")
            return None

    def verify_path(self, path: str) -> bool:
        """Verify path exists and is accessible"""
        try:
            # Check network availability
            if not self.network_available:
                return False
                
            # Normalize and check path
            normalized_path = self.normalize_path(path)
            return os.path.exists(normalized_path)

        except Exception as e:
            logging.error(f"Error verifying path {path}: {str(e)}")
            return False

    def get_subfolders(self, path: str) -> List[str]:
        """Get list of subfolders in directory"""
        try:
            if not self.verify_path(path):
                return []
                
            return [d for d in os.listdir(path) 
                   if os.path.isdir(os.path.join(path, d))]

        except Exception as e:
            logging.error(f"Error getting subfolders for {path}: {str(e)}")
            return []

    def get_folder_structure(self, path: str, max_depth: int = -1) -> Dict:
        """Get hierarchical folder structure"""
        structure = {}
        try:
            if not self.verify_path(path) or max_depth == 0:
                return structure

            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    structure[item] = self.get_folder_structure(
                        item_path, 
                        max_depth - 1 if max_depth > 0 else -1
                    )

            return structure

        except Exception as e:
            logging.error(f"Error getting folder structure for {path}: {str(e)}")
            return structure

    def create_path_tree(self, paths: List[str]) -> Dict:
        """Create tree structure from list of paths"""
        tree = {}
        try:
            for path in paths:
                current = tree
                parts = self.get_relative_path(path).split('/')
                
                for part in parts:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                    
            return tree

        except Exception as e:
            logging.error(f"Error creating path tree: {str(e)}")
            return {}

    def monitor_network_status(self):
        """Monitor network connection status"""
        previous_status = self.network_available
        current_status = self.verify_network_access()
        
        if current_status != previous_status:
            if current_status:
                logging.info("Network connection restored")
            else:
                logging.warning("Network connection lost")
                
        return current_status


