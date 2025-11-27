"""
Main Excel Analysis Agent
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from .utils.file_manager import FileManager
from .preprocessing import UnmergeProcessor, HeaderAnalyzer, TableNormalizer
from .nlp import IntentExtractor, ColumnMapper
from .codegen import CodeGenerator, CodeExecutor
from .lineage import LineageTracker


class ExcelAnalysisAgent:
    """Main agent that orchestrates the entire analysis pipeline"""
    
    def __init__(self, excel_dir: Optional[str] = None, data_dir: str = "data"):
        """
        Initialize the analysis agent
        
        Args:
            excel_dir: Optional directory containing Excel files (if None, no preprocessing on init)
            data_dir: Directory to store preprocessed tables
        """
        self.excel_dir = excel_dir
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.file_manager = None  # Will be created when needed
        if excel_dir:
            self.file_manager = FileManager(excel_dir)
        self.unmerge_processor = None  # Will be created per file
        self.header_analyzer = HeaderAnalyzer()
        self.table_normalizer = TableNormalizer()
        self.intent_extractor = IntentExtractor()
        self.column_mapper = ColumnMapper()
        self.code_generator = CodeGenerator(llm_client=None)  # Will auto-initialize OpenAI if API key available
        self.code_executor = CodeExecutor()
        self.lineage_tracker = LineageTracker()
        
        # Cache for normalized tables
        self.normalized_tables: List[Dict] = []
        
        # Only preprocess if excel_dir is provided
        if excel_dir:
            self._preprocess_all_files()
    
    def _preprocess_all_files(self):
        """Preprocess all Excel files and create normalized tables"""
        if not self.file_manager:
            print("No file manager initialized. Skipping preprocessing.")
            return
        
        print("Preprocessing Excel files...")
        
        excel_files = self.file_manager.list_excel_files()
        
        if not excel_files:
            print("No Excel files found in the directory.")
            return
        
        for file_path in excel_files:
            print(f"\nProcessing: {file_path.name}")
            
            try:
                sheets = self.file_manager.get_sheet_names(file_path)
                
                for sheet_name in sheets:
                    print(f"  Processing sheet: {sheet_name}")
                    
                    # Step 1: Unmerge cells
                    unmerge_processor = UnmergeProcessor(str(file_path))
                    df_unmerged = unmerge_processor.process_sheet(sheet_name)
                    
                    # Step 2: Get sample rows for header analysis
                    sample_df = unmerge_processor.get_sample_rows(df_unmerged, n=10)
                    
                    # Step 3: Classify rows (labels vs headers)
                    classification = self.header_analyzer.analyze_headers(sample_df, sheet_name)
                    print(f"    Classification: {classification}")
                    
                    # Step 4: Normalize table
                    normalized_df, metadata = self.table_normalizer.normalize_table(
                        df_unmerged, 
                        classification
                    )
                    
                    # Step 5: Save normalized table
                    table_name = f"{file_path.stem}_{sheet_name}"
                    table_path = self.data_dir / f"{table_name}.parquet"
                    
                    # Convert all columns to string to avoid parquet type issues
                    # This preserves all data and avoids conversion errors
                    normalized_df_str = normalized_df.astype(str).replace('nan', '')
                    normalized_df_str.to_parquet(table_path, index=False)
                    
                    # Store metadata
                    table_info = {
                        "name": table_name,
                        "file_path": str(table_path),
                        "file_name": file_path.name,
                        "sheet_name": sheet_name,
                        "columns": list(normalized_df.columns),
                        "column_types": metadata.get("column_types", {}),
                        "row_count": len(normalized_df),
                        "metadata": metadata
                    }
                    
                    self.normalized_tables.append(table_info)
                    print(f"    Normalized: {len(normalized_df)} rows, {len(normalized_df.columns)} columns")
            
            except Exception as e:
                print(f"  Error processing {file_path.name}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\nPreprocessing complete. {len(self.normalized_tables)} normalized tables created.")
    
    def analyze(self, question: str) -> Dict:
        """
        Analyze a user question and return results
        
        Args:
            question: User's natural language question
        
        Returns:
            Dictionary containing:
            - code: Generated Python code
            - execution_result: Execution results
            - lineage: Data lineage report
            - success: Whether analysis succeeded
        """
        print(f"\n{'='*60}")
        print(f"Analyzing question: {question}")
        print(f"{'='*60}\n")
        
        # Check if we have any tables
        if not self.normalized_tables:
            return {
                "success": False,
                "error": "No Excel files have been uploaded. Please upload files first.",
                "code": None,
                "execution_result": None,
                "lineage": None
            }
        
        # Step 1: Extract intent
        print("Step 1: Extracting intent...")
        intent = self.intent_extractor.extract_intent(question, self.normalized_tables)
        print(f"  Intent: {intent['intent_type']}")
        print(f"  Operations: {intent.get('operations', [])}")
        print(f"  Group by: {intent.get('group_by', [])}")
        
        # Step 2: Map entities to columns
        print("\nStep 2: Mapping entities to columns...")
        entity_mapping = self.column_mapper.map_entities_to_columns(
            intent.get("entities", {}),
            self.normalized_tables,
            intent
        )
        
        # Infer additional columns from intent
        inferred_mapping = self.column_mapper.infer_columns_from_intent(
            intent,
            self.normalized_tables
        )
        
        # Merge mappings
        column_mapping = {**entity_mapping, **inferred_mapping}
        print(f"  Column mapping: {column_mapping}")
        
        # Step 3: Select table
        selected_table = self._select_table(intent)
        if not selected_table:
            return {
                "success": False,
                "error": "No suitable table found for analysis",
                "code": None,
                "execution_result": None,
                "lineage": None
            }
        
        print(f"\nStep 3: Selected table: {selected_table['name']}")
        
        # Step 4: Generate code
        print("\nStep 4: Generating Python code...")
        code, lineage_info = self.code_generator.generate_code(
            intent,
            column_mapping,
            selected_table,
            question
        )
        
        print("\nGenerated code:")
        print("-" * 60)
        print(code)
        print("-" * 60)
        
        # Step 5: Execute code
        print("\nStep 5: Executing code...")
        execution_result = self.code_executor.execute_with_error_handling(
            code,
            column_mapping
        )
        
        if execution_result["success"]:
            print("Execution successful!")
            if execution_result.get("output"):
                print("\nOutput:")
                print(execution_result["output"])
        else:
            print("Execution failed!")
            print(f"Error: {execution_result['error']}")
            if execution_result.get("suggestions"):
                print("\nSuggestions:")
                for suggestion in execution_result["suggestions"]:
                    print(f"  - {suggestion}")
        
        # Step 6: Create lineage report
        print("\nStep 6: Creating lineage report...")
        lineage_report = self.lineage_tracker.create_lineage_report(
            lineage_info,
            execution_result
        )
        
        print("\nData Lineage:")
        print(self.lineage_tracker.format_lineage_for_display(lineage_report))
        
        return {
            "success": execution_result["success"],
            "question": question,
            "code": code,
            "execution_result": execution_result,
            "lineage": lineage_report,
            "intent": intent,
            "column_mapping": column_mapping
        }
    
    def _select_table(self, intent: Dict) -> Optional[Dict]:
        """Select the most relevant table based on intent"""
        selected_tables = intent.get("selected_tables", [])
        
        if selected_tables:
            # Use explicitly selected tables
            for table in self.normalized_tables:
                if table["name"] in selected_tables:
                    return table
        
        # If no selection, use first table
        if self.normalized_tables:
            return self.normalized_tables[0]
        
        return None

