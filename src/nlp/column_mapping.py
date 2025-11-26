"""
Map natural language entities to concrete Excel columns
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
from difflib import SequenceMatcher


class ColumnMapper:
    """Maps entities to actual columns in tables"""
    
    def __init__(self):
        """Initialize column mapper"""
        pass
    
    def map_entities_to_columns(
        self, 
        entities: Dict[str, List[str]], 
        tables: List[Dict],
        intent: Dict
    ) -> Dict[str, str]:
        """
        Map extracted entities to actual column names
        
        Args:
            entities: Dictionary mapping entity types to possible names
            tables: List of table metadata
            intent: Extracted intent
        
        Returns:
            Dictionary mapping entity types to actual column names
        """
        mapping = {}
        
        # Get selected tables
        selected_tables = intent.get("selected_tables", [])
        if not selected_tables and tables:
            # If no tables selected, use first table
            selected_tables = [tables[0]]
        else:
            # Filter tables
            selected_tables = [t for t in tables if t.get("name") in selected_tables]
        
        if not selected_tables:
            return mapping
        
        # For each entity type, find best matching column
        for entity_type, possible_names in entities.items():
            best_match = self._find_best_column_match(
                entity_type, 
                possible_names, 
                selected_tables
            )
            if best_match:
                mapping[entity_type] = best_match
        
        return mapping
    
    def _find_best_column_match(
        self, 
        entity_type: str, 
        possible_names: List[str], 
        tables: List[Dict]
    ) -> Optional[str]:
        """
        Find best matching column for an entity
        
        Args:
            entity_type: Type of entity (e.g., "region", "sales")
            possible_names: Possible names for this entity
            tables: Available tables
        
        Returns:
            Best matching column name or None
        """
        best_score = 0.0
        best_column = None
        
        for table in tables:
            columns = table.get("columns", [])
            
            for col in columns:
                # Calculate similarity with each possible name
                for name in possible_names:
                    score = self._similarity_score(name.lower(), col.lower())
                    
                    # Boost score if entity type matches column name pattern
                    if entity_type.lower() in col.lower():
                        score += 0.2
                    
                    if score > best_score:
                        best_score = score
                        best_column = col
        
        # Only return if similarity is above threshold
        if best_score > 0.3:
            return best_column
        
        return None
    
    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def infer_columns_from_intent(
        self, 
        intent: Dict, 
        tables: List[Dict]
    ) -> Dict[str, str]:
        """
        Infer which columns to use based on intent
        
        Args:
            intent: Extracted intent
            tables: Available tables
        
        Returns:
            Dictionary mapping roles to column names
        """
        column_mapping = {}
        
        # Get selected tables
        selected_tables = intent.get("selected_tables", [])
        if not selected_tables and tables:
            selected_tables = [tables[0]]
        else:
            selected_tables = [t for t in tables if t.get("name") in selected_tables]
        
        if not selected_tables:
            return column_mapping
        
        # Get all columns from selected tables
        all_columns = []
        for table in selected_tables:
            all_columns.extend(table.get("columns", []))
        
        # Infer group_by columns
        group_by = intent.get("group_by", [])
        for gb in group_by:
            match = self._find_best_column_match(gb, [gb], selected_tables)
            if match:
                column_mapping[f"group_by_{gb}"] = match
        
        # Infer metric columns (for aggregation)
        operations = intent.get("operations", [])
        if operations:
            # Try to find numeric columns that might be metrics
            for table in selected_tables:
                column_types = table.get("column_types", {})
                numeric_cols = [
                    col for col in table.get("columns", [])
                    if column_types.get(col) == "numeric"
                ]
                if numeric_cols:
                    # Use first numeric column as default metric
                    column_mapping["metric"] = numeric_cols[0]
                    break
        
        # Infer date columns (for trend analysis)
        if intent.get("intent_type") == "trend":
            for table in selected_tables:
                column_types = table.get("column_types", {})
                date_cols = [
                    col for col in table.get("columns", [])
                    if column_types.get(col) == "datetime"
                ]
                if date_cols:
                    column_mapping["date"] = date_cols[0]
                    break
        
        return column_mapping

