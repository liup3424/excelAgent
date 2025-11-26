"""
File management utilities for Excel files
"""

import os
from pathlib import Path
from typing import List, Optional
import pandas as pd


class FileManager:
    """Manages Excel files in the knowledge base"""
    
    def __init__(self, excel_dir: str = "excelExample"):
        """
        Initialize file manager
        
        Args:
            excel_dir: Directory containing Excel files
        """
        self.excel_dir = Path(excel_dir)
        if not self.excel_dir.exists():
            raise ValueError(f"Excel directory not found: {excel_dir}")
    
    def list_excel_files(self) -> List[Path]:
        """List all Excel files in the directory"""
        excel_extensions = ['.xlsx', '.xls', '.xlsm']
        files = []
        for ext in excel_extensions:
            files.extend(self.excel_dir.glob(f"*{ext}"))
        return sorted(files)
    
    def get_file_info(self, file_path: Path) -> dict:
        """Get metadata about an Excel file"""
        return {
            "path": str(file_path),
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "sheets": self.get_sheet_names(file_path)
        }
    
    def get_sheet_names(self, file_path: Path) -> List[str]:
        """Get list of sheet names in an Excel file"""
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return []
    
    def load_raw_sheet(self, file_path: Path, sheet_name: str, header: Optional[int] = None) -> pd.DataFrame:
        """
        Load a raw sheet without preprocessing
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of the sheet
            header: Row to use as header (None for no header)
        
        Returns:
            DataFrame with raw data
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header)
            return df
        except Exception as e:
            raise ValueError(f"Error loading sheet {sheet_name} from {file_path}: {e}")

