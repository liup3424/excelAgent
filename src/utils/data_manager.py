"""
Data Manager - Singleton to hold normalized tables
"""

from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd


class DataManager:
    """Singleton class to manage normalized tables"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.tables: List[Dict] = []
            self.workspace_dir = Path("workspace")
            self.uploads_dir = self.workspace_dir / "uploads"
            self.charts_dir = self.workspace_dir / "charts"
            self._initialized = True
    
    def initialize_directories(self):
        """Create necessary directories"""
        self.workspace_dir.mkdir(exist_ok=True)
        self.uploads_dir.mkdir(exist_ok=True)
        self.charts_dir.mkdir(exist_ok=True)
    
    def add_table(self, table_info: Dict):
        """Add a normalized table to the manager"""
        self.tables.append(table_info)
    
    def clear_tables(self):
        """Clear all tables and associated files"""
        import shutil
        
        # Clear in-memory tables
        self.tables = []
        
        # Clear parquet files
        data_dir = self.workspace_dir / "data"
        if data_dir.exists():
            for parquet_file in data_dir.glob("*.parquet"):
                try:
                    parquet_file.unlink()
                except Exception as e:
                    print(f"Warning: Could not delete {parquet_file}: {e}")
        
        # Clear uploaded files
        if self.uploads_dir.exists():
            for upload_file in self.uploads_dir.glob("*"):
                if upload_file.is_file():
                    try:
                        upload_file.unlink()
                    except Exception as e:
                        print(f"Warning: Could not delete {upload_file}: {e}")
        
        # Clear chart files
        if self.charts_dir.exists():
            for chart_file in self.charts_dir.glob("*"):
                if chart_file.is_file():
                    try:
                        chart_file.unlink()
                    except Exception as e:
                        print(f"Warning: Could not delete {chart_file}: {e}")
        
        print("Cleared all tables and associated files.")
    
    def get_tables(self) -> List[Dict]:
        """Get all normalized tables"""
        return self.tables
    
    def get_table_by_name(self, name: str) -> Optional[Dict]:
        """Get a table by name"""
        for table in self.tables:
            if table.get("name") == name:
                return table
        return None
    
    def get_all_table_info(self) -> List[Dict]:
        """Get summary info for all tables"""
        return [
            {
                "name": t.get("name", "Unknown"),
                "file_name": t.get("file_name", "Unknown"),
                "sheet_name": t.get("sheet_name", "Unknown"),
                "columns": t.get("columns", []),
                "row_count": t.get("row_count", 0)
            }
            for t in self.tables
        ]

