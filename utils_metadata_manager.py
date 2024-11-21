import pandas as pd
import os
import json
from datetime import datetime
import logging
from typing import Dict, Optional, List
from pathlib import Path

class MetadataManager:
    def add_files_basic_metadata(self, file_paths: list) -> bool:
        """Add basic metadata for files to database"""
        try:
            # Create backup before modifying
            self.backup_current_metadata()
            
            # Create new entries for each file
            for file_path in file_paths:
                metadata = {
                    # Basic file information
                    'file_path': file_path,
                    'file_name': os.path.basename(file_path),
                    'file_location': os.path.dirname(file_path),
                    'file_extension': os.path.splitext(file_path)[1].lower(),
                    'file_size': os.path.getsize(file_path),
                    'date_added': datetime.now(),
                    'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)),
                    
                    # Initialize other fields as empty
                    'project_number': '',
                    'department': '',
                    'area': '',
                    'type': '',
                    'source': '',
                    'revision': '',
                    'issue_status': '',
                    'work_status': '',
                    'scale': '',
                    'paper_size': '',
                    'applicable_codes': '',
                    'equipment_tags': '',
                    'related_documents': '',
                    'priority': '',
                    'milestone': '',
                    'contract_phase': '',
                    'budget_code': '',
                    'deliverable_id': '',
                    'approved_by': '',
                    'comments': ''
                }
                
                # Remove existing entry if it exists
                self.metadata_df = self.metadata_df[
                    self.metadata_df['file_path'] != file_path
                ]
                
                # Add new entry
                self.metadata_df = pd.concat([
                    self.metadata_df, 
                    pd.DataFrame([metadata])
                ], ignore_index=True)
            
            # Save to Excel file
            return self.save_database()
            
        except Exception as e:
            logging.error(f"Error adding basic metadata: {str(e)}")
            return False
        

    def __init__(self, safety_manager, local_storage_path: str = "local_metadata"):
        self.safety = safety_manager
        self.local_storage_path = local_storage_path
        self.metadata_file = os.path.join(local_storage_path, "metadata.xlsx")
        self.backup_dir = os.path.join(local_storage_path, "backups")
        self.metadata_cache = {}
        self.setup_storage()
        self.setup_logging()


    def setup_storage(self):
        """Initialize local storage directories"""
        try:
            os.makedirs(self.local_storage_path, exist_ok=True)
            os.makedirs(self.backup_dir, exist_ok=True)
            
            if not os.path.exists(self.metadata_file):
                self.create_new_metadata_file()
            
            self.metadata_df = pd.read_excel(self.metadata_file)
            
        except Exception as e:
            logging.error(f"Error setting up metadata storage: {str(e)}")
            self.metadata_df = pd.DataFrame()


    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            filename=os.path.join(self.local_storage_path, 'metadata_operations.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )


    def create_new_metadata_file(self):
        """Create new metadata file with predefined structure"""
        columns = [
            'file_path',
            'project_number',
            'department',
            'area',
            'type',
            'source',
            'revision',
            'status',
            'created_date',
            'modified_date',
            'file_size',
            'checksum',
            'last_indexed'
        ]
        df = pd.DataFrame(columns=columns)
        df.to_excel(self.metadata_file, index=False)


    def read_metadata(self, file_path: str) -> Optional[Dict]:
        """Read metadata for specific file (read-only operation)"""
        try:
            if not self.safety.safe_read_operation(file_path):
                return None

            # Check cache first
            if file_path in self.metadata_cache:
                return self.metadata_cache[file_path].copy()

            # Query dataframe
            file_data = self.metadata_df[
                self.metadata_df['file_path'] == file_path
            ]

            if file_data.empty:
                return self.create_default_metadata(file_path)

            metadata = file_data.iloc[0].to_dict()
            self.metadata_cache[file_path] = metadata.copy()
            return metadata

        except Exception as e:
            logging.error(f"Error reading metadata for {file_path}: {str(e)}")
            return None

    def create_default_metadata(self, file_path: str) -> Dict:
        """Create default metadata for new file"""
        return {
            'file_path': file_path,
            'created_date': datetime.now(),
            'modified_date': datetime.now(),
            'last_indexed': datetime.now(),
            'status': 'Indexed',
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }

    def update_metadata(self, file_path: str, metadata: Dict) -> bool:
        """Update metadata in local storage"""
        try:
            if self.safety.is_protected_path(file_path):
                logging.warning(f"Attempted to update metadata for protected path: {file_path}")
                return False

            metadata['modified_date'] = datetime.now()
            metadata['file_path'] = file_path

            # Update DataFrame
            self.metadata_df = self.metadata_df[
                self.metadata_df['file_path'] != file_path
            ]
            
            self.metadata_df = pd.concat([
                self.metadata_df, 
                pd.DataFrame([metadata])
            ], ignore_index=True)

            # Update cache
            self.metadata_cache[file_path] = metadata.copy()

            # Save to local storage
            self.backup_current_metadata()
            self.metadata_df.to_excel(self.metadata_file, index=False)
            
            return True

        except Exception as e:
            logging.error(f"Error updating metadata for {file_path}: {str(e)}")
            return False

    def backup_current_metadata(self):
        """Create backup of current metadata"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(
                self.backup_dir, 
                f"metadata_backup_{timestamp}.xlsx"
            )
            self.metadata_df.to_excel(backup_path, index=False)
            self.cleanup_old_backups()
        except Exception as e:
            logging.error(f"Error creating metadata backup: {str(e)}")

    def cleanup_old_backups(self, max_backups: int = 10):
        """Remove old backup files"""
        try:
            backups = sorted([
                os.path.join(self.backup_dir, f) 
                for f in os.listdir(self.backup_dir)
            ])
            
            while len(backups) > max_backups:
                os.remove(backups.pop(0))
        except Exception as e:
            logging.error(f"Error cleaning up backups: {str(e)}")

    def search_metadata(self, criteria: Dict) -> pd.DataFrame:
        """Search metadata based on criteria (read-only operation)"""
        try:
            result = self.metadata_df.copy()
            
            for field, value in criteria.items():
                if value:
                    if isinstance(value, list):
                        result = result[result[field].isin(value)]
                    else:
                        result = result[result[field].str.contains(
                            str(value), 
                            case=False, 
                            na=False
                        )]
            
            return result
            
        except Exception as e:
            logging.error(f"Error searching metadata: {str(e)}")
            return pd.DataFrame()

    def get_unique_values(self, field: str) -> List:
        """Get unique values for a field (read-only operation)"""
        try:
            if field in self.metadata_df.columns:
                return sorted(self.metadata_df[field].unique().tolist())
            return []
        except Exception as e:
            logging.error(f"Error getting unique values: {str(e)}")
            return []

    def clear_cache(self):
        """Clear metadata cache"""
        self.metadata_cache.clear()