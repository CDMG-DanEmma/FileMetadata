import pandas as pd
import os
from datetime import datetime
import logging
from typing import Dict, Optional, List
from pathlib import Path

class MetadataModel:
    def __init__(self, safety_manager, excel_path: str = "metadata.xlsx"):
        self.safety = safety_manager
        self.excel_path = excel_path
        self.metadata_df = None
        self.backup_dir = "metadata_backups"
        self.metadata_cache = {}
        self.setup_model()
        self.setup_logging()

    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            filename='metadata_operations.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_model(self):
        """Initialize metadata model"""
        try:
            os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)
            os.makedirs(self.backup_dir, exist_ok=True)
            
            if os.path.exists(self.excel_path):
                self.metadata_df = pd.read_excel(self.excel_path)
            else:
                self.create_new_database()
                
        except Exception as e:
            logging.error(f"Error initializing metadata model: {str(e)}")
            self.create_new_database()

    def create_new_database(self):
        """Create new metadata database with predefined columns"""
        self.metadata_df = pd.DataFrame(columns=[
            # Basic file information
            'file_path',
            'file_name',
            'file_location',
            'file_extension',
            'file_size',
            'date_added',
            'last_modified',
            
            # Project information
            'project_number',
            'department',
            'area',
            
            # Document properties
            'type',
            'source',
            'revision',
            'issue_status',
            'work_status',
            'scale',
            'paper_size',
            
            # Technical reference
            'applicable_codes',
            'equipment_tags',
            'related_documents',
            
            # Administrative
            'priority',
            'milestone',
            'contract_phase',
            'budget_code',
            'deliverable_id',
            'approved_by',
            'comments'
        ])
        self.save_database()

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

    def save_database(self) -> bool:
        """Save metadata to Excel file"""
        try:
            self.metadata_df.to_excel(self.excel_path, index=False)
            return True
        except Exception as e:
            logging.error(f"Error saving metadata: {str(e)}")
            return False

    def backup_current_metadata(self):
        """Create backup of current metadata"""
        try:
            if os.path.exists(self.excel_path):
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

    def get_metadata(self, file_path: str) -> Optional[Dict]:
        """Retrieve metadata for specific file"""
        try:
            # Check cache first
            if file_path in self.metadata_cache:
                return self.metadata_cache[file_path].copy()

            # Query dataframe
            file_data = self.metadata_df[
                self.metadata_df['file_path'] == file_path
            ]

            if file_data.empty:
                return None

            metadata = file_data.iloc[0].to_dict()
            self.metadata_cache[file_path] = metadata.copy()
            return metadata

        except Exception as e:
            logging.error(f"Error retrieving metadata for {file_path}: {str(e)}")
            return None

    def search_metadata(self, search_terms: Dict) -> pd.DataFrame:
        """Search metadata based on criteria"""
        try:
            result = self.metadata_df.copy()
            
            for field, value in search_terms.items():
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
        """Get unique values for a field"""
        try:
            if field in self.metadata_df.columns:
                return sorted(self.metadata_df[field].dropna().unique().tolist())
            return []
        except Exception as e:
            logging.error(f"Error getting unique values: {str(e)}")
            return []

    def update_metadata(self, file_path: str, metadata: Dict) -> bool:
        """Update metadata for specific file"""
        try:
            if self.safety.is_protected_path(file_path):
                logging.warning(f"Attempted to update protected file metadata: {file_path}")
                return False

            # Update timestamp
            metadata['last_modified'] = datetime.now()

            # Remove existing entry
            self.metadata_df = self.metadata_df[
                self.metadata_df['file_path'] != file_path
            ]
            
            # Add updated entry
            self.metadata_df = pd.concat([
                self.metadata_df, 
                pd.DataFrame([metadata])
            ], ignore_index=True)

            # Update cache
            self.metadata_cache[file_path] = metadata.copy()

            # Save changes
            self.backup_current_metadata()
            return self.save_database()

        except Exception as e:
            logging.error(f"Error updating metadata for {file_path}: {str(e)}")
            return False

    def clear_cache(self):
        """Clear metadata cache"""
        self.metadata_cache.clear()

    def get_file_count(self) -> int:
        """Get total number of files in database"""
        return len(self.metadata_df)

    def get_statistics(self) -> Dict:
        """Get basic statistics about the metadata database"""
        try:
            return {
                'total_files': len(self.metadata_df),
                'departments': self.get_unique_values('department'),
                'file_types': self.get_unique_values('type'),
                'newest_file': self.metadata_df['date_added'].max(),
                'oldest_file': self.metadata_df['date_added'].min()
            }
        except Exception as e:
            logging.error(f"Error getting statistics: {str(e)}")
            return {}