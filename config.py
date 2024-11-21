import os
import json
import logging
from typing import Dict, List, Optional

class Config:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.settings = self.load_config()

    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return self.get_default_config()
        except Exception as e:
            logging.error(f"Error loading config: {str(e)}")
            return self.get_default_config()

    def save_config(self) -> bool:
        """Save current configuration to JSON file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            logging.error(f"Error saving config: {str(e)}")
            return False

    def get_default_config(self) -> Dict:
        """Return default configuration settings"""
        return {
            "network_paths": {
                "root": "P:/",
                "projects": "P:/Projects",
                "templates": "P:/Templates"
            },
            "metadata": {
                "path": "metadata.xlsx",
                "backup_dir": "metadata_backups"
            },
            "ui": {
                "window_size": [1200, 800],
                "theme": "system",
                "recent_searches": []
            },
            "file_types": {
                "drawing": [".dwg", ".pdf", ".rvt"],
                "document": [".doc", ".docx", ".pdf"],
                "spreadsheet": [".xls", ".xlsx"]
            }
        }

    def get_network_paths(self) -> Dict[str, str]:
        """Return configured network paths"""
        return self.settings.get("network_paths", {})

    def get_metadata_settings(self) -> Dict:
        """Return metadata configuration"""
        return self.settings.get("metadata", {})

    def get_ui_settings(self) -> Dict:
        """Return UI configuration"""
        return self.settings.get("ui", {})

    def update_setting(self, key: str, value: any) -> bool:
        """Update specific configuration setting"""
        try:
            self.settings[key] = value
            return self.save_config()
        except Exception as e:
            logging.error(f"Error updating setting: {str(e)}")
            return False

    def add_recent_search(self, search_term: str):
        """Add search term to recent searches list"""
        recent = self.settings["ui"]["recent_searches"]
        if search_term in recent:
            recent.remove(search_term)
        recent.insert(0, search_term)
        self.settings["ui"]["recent_searches"] = recent[:10]
        self.save_config()

    @staticmethod
    def create_default():
        """Helper function to create and return Config instance"""
        return Config()