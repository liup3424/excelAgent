"""
Clean and merge headers, normalize to 2D tables
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import re


class TableNormalizer:
    """Normalizes Excel sheets to clean 2D tables"""
    
    def __init__(self):
        """Initialize normalizer"""
        pass
    
    def remove_label_rows(self, df: pd.DataFrame, label_indices: List[int]) -> pd.DataFrame:
        """
        Remove rows classified as labels
        
        Args:
            df: DataFrame
            label_indices: 1-based row indices to remove
        
        Returns:
            DataFrame with label rows removed
        """
        if not label_indices:
            return df.copy()
        
        # Convert 1-based indices to 0-based
        indices_to_drop = [idx - 1 for idx in label_indices if idx > 0]
        
        # Filter out invalid indices
        valid_indices = [idx for idx in indices_to_drop if idx < len(df)]
        
        if not valid_indices:
            return df.copy()
        
        # Drop rows
        df_cleaned = df.drop(df.index[valid_indices]).reset_index(drop=True)
        
        return df_cleaned
    
    def merge_multi_level_headers(self, df: pd.DataFrame, header_indices: List[int]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Merge multi-level headers into a single header row
        
        Args:
            df: DataFrame
            header_indices: 1-based row indices that form the header
        
        Returns:
            Tuple of (DataFrame with merged header, header metadata)
        """
        if not header_indices:
            # No header rows specified, use first row as header
            if len(df) == 0:
                # Empty dataframe
                return df.copy(), self._create_header_metadata([])
            header_df = df.head(1)
            if len(df) > 1:
                data_df = df.iloc[1:].reset_index(drop=True)
            else:
                data_df = pd.DataFrame(columns=df.columns)
            # Set column names from first row
            if len(header_df) > 0:
                data_df.columns = header_df.iloc[0].values
            return data_df, self._create_header_metadata(header_df.iloc[0] if len(header_df) > 0 else [])
        
        # Convert 1-based to 0-based
        header_row_indices = [idx - 1 for idx in header_indices if idx > 0]
        header_row_indices = [idx for idx in header_row_indices if idx < len(df)]
        
        if not header_row_indices:
            # Invalid indices, use first row
            header_df = df.head(1)
            data_df = df.iloc[1:].reset_index(drop=True)
            data_df.columns = header_df.iloc[0].values
            return data_df, self._create_header_metadata(header_df.iloc[0])
        
        # Extract header rows
        header_rows = df.iloc[header_row_indices].copy()
        
        # Merge header rows into single row
        merged_header = self._merge_header_rows(header_rows)
        
        # Get data rows (rows after the last header row)
        last_header_idx = max(header_row_indices)
        data_df = df.iloc[last_header_idx + 1:].copy().reset_index(drop=True)
        
        # Set merged header as column names
        data_df.columns = merged_header
        
        # Create metadata
        header_metadata = self._create_header_metadata(merged_header, header_rows)
        
        return data_df, header_metadata
    
    def _merge_header_rows(self, header_rows: pd.DataFrame) -> List[str]:
        """
        Merge multiple header rows into a single header
        
        Strategy:
        1. Forward-fill parent headers (non-empty values propagate down)
        2. Concatenate non-empty parts with underscore delimiter
        
        Args:
            header_rows: DataFrame containing header rows
        
        Returns:
            List of merged header names
        """
        if len(header_rows) == 0:
            return []
        
        if len(header_rows) == 1:
            # Single header row
            return [str(val) if pd.notna(val) and str(val).strip() else f"Column_{i+1}" 
                   for i, val in enumerate(header_rows.iloc[0].values)]
        
        # Multiple header rows - merge them
        num_cols = len(header_rows.columns)
        merged = []
        
        for col_idx in range(num_cols):
            # Get values for this column across all header rows
            col_values = []
            for row_idx in range(len(header_rows)):
                val = header_rows.iloc[row_idx, col_idx]
                if pd.notna(val) and str(val).strip():
                    col_values.append(str(val).strip())
            
            # Join non-empty values with underscore
            if col_values:
                merged_name = "_".join(col_values)
            else:
                merged_name = f"Column_{col_idx + 1}"
            
            merged.append(merged_name)
        
        # Clean up merged names
        merged = [self._clean_column_name(name) for name in merged]
        
        # Ensure uniqueness
        merged = self._ensure_unique_column_names(merged)
        
        return merged
    
    def _clean_column_name(self, name: str) -> str:
        """Clean column name"""
        # Remove extra whitespace
        name = re.sub(r'\s+', '_', name.strip())
        # Remove special characters that might cause issues
        name = re.sub(r'[^\w\s-]', '', name)
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        # Remove leading/trailing underscores
        name = name.strip('_')
        return name if name else "Unnamed"
    
    def _ensure_unique_column_names(self, names: List[str]) -> List[str]:
        """Ensure all column names are unique"""
        seen = {}
        result = []
        
        for name in names:
            if name in seen:
                seen[name] += 1
                result.append(f"{name}_{seen[name]}")
            else:
                seen[name] = 0
                result.append(name)
        
        return result
    
    def _create_header_metadata(self, header: List, header_rows: Optional[pd.DataFrame] = None) -> Dict:
        """Create metadata about the header"""
        return {
            "original_header_rows": len(header_rows) if header_rows is not None else 1,
            "column_count": len(header),
            "column_names": list(header)
        }
    
    def normalize_table(self, df: pd.DataFrame, classification: Dict[str, List[int]]) -> Tuple[pd.DataFrame, Dict]:
        """
        Complete normalization pipeline
        
        Args:
            df: Raw DataFrame (after unmerging)
            classification: Dictionary with 'labels' and 'header' keys
        
        Returns:
            Tuple of (normalized DataFrame, metadata)
        """
        # Step 1: Remove label rows
        df_no_labels = self.remove_label_rows(df, classification.get("labels", []))
        
        # Step 2: Merge headers and extract data
        normalized_df, header_metadata = self.merge_multi_level_headers(
            df_no_labels, 
            classification.get("header", [])
        )
        
        # Step 3: Clean data
        normalized_df = self._clean_dataframe(normalized_df)
        
        # Step 4: Infer column types
        column_types = self._infer_column_types(normalized_df)
        
        metadata = {
            "header": header_metadata,
            "column_types": column_types,
            "row_count": len(normalized_df),
            "column_count": len(normalized_df.columns)
        }
        
        return normalized_df, metadata
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame: remove empty rows/columns, handle NaN"""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Remove completely empty columns
        df = df.dropna(axis=1, how='all')
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def _infer_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """Infer column types"""
        types = {}
        
        for col in df.columns:
            col_data = df[col].dropna()
            
            if len(col_data) == 0:
                types[col] = "empty"
            elif pd.api.types.is_numeric_dtype(df[col]):
                types[col] = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                types[col] = "datetime"
            else:
                # Try to parse as date
                try:
                    pd.to_datetime(col_data.head(10))
                    types[col] = "datetime"
                except:
                    types[col] = "categorical"
        
        return types

