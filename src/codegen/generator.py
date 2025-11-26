"""
Generate Python code for data analysis
"""

from typing import Dict, List, Optional, Tuple
import json


class CodeGenerator:
    """Generates Python code for analysis"""
    
    def __init__(self):
        """Initialize code generator"""
        pass
    
    def generate_code(
        self, 
        intent: Dict, 
        column_mapping: Dict[str, str],
        table_info: Dict,
        question: str
    ) -> Tuple[str, Dict]:
        """
        Generate Python code for analysis
        
        Args:
            intent: Extracted intent
            column_mapping: Mapping of entities to columns
            table_info: Information about the table to analyze
            question: Original user question
        
        Returns:
            Tuple of (generated code, metadata about columns used)
        """
        code_parts = []
        lineage_info = {
            "columns_used": [],
            "operations": [],
            "file_name": table_info.get("file_name", ""),
            "sheet_name": table_info.get("sheet_name", "")
        }
        
        # Import statements
        code_parts.append("import pandas as pd")
        code_parts.append("import numpy as np")
        code_parts.append("import matplotlib.pyplot as plt")
        code_parts.append("import plotly.express as px")
        code_parts.append("import plotly.graph_objects as go")
        code_parts.append("")
        
        # Load data
        load_code, load_lineage = self._generate_load_code(table_info)
        code_parts.append(load_code)
        lineage_info["columns_used"].extend(load_lineage.get("columns", []))
        code_parts.append("")
        
        # Apply filters
        if intent.get("filters"):
            filter_code, filter_lineage = self._generate_filter_code(intent["filters"], column_mapping)
            code_parts.append(filter_code)
            lineage_info["columns_used"].extend(filter_lineage.get("columns", []))
            code_parts.append("")
        
        # Group by and aggregate
        if intent.get("group_by") or intent.get("operations"):
            agg_code, agg_lineage = self._generate_aggregation_code(intent, column_mapping)
            code_parts.append(agg_code)
            lineage_info["columns_used"].extend(agg_lineage.get("columns", []))
            lineage_info["operations"].extend(agg_lineage.get("operations", []))
            code_parts.append("")
        
        # Sort
        if intent.get("sort"):
            sort_code, sort_lineage = self._generate_sort_code(intent["sort"], column_mapping)
            code_parts.append(sort_code)
            lineage_info["columns_used"].extend(sort_lineage.get("columns", []))
            code_parts.append("")
        
        # Visualization
        if intent.get("intent_type") in ["visualization", "trend", "comparison"]:
            viz_code, viz_lineage = self._generate_visualization_code(intent, column_mapping)
            code_parts.append(viz_code)
            lineage_info["columns_used"].extend(viz_lineage.get("columns", []))
            code_parts.append("")
        
        # Display results
        display_code = self._generate_display_code(intent)
        code_parts.append(display_code)
        
        # Combine code
        full_code = "\n".join(code_parts)
        
        # Remove duplicates from columns_used
        lineage_info["columns_used"] = list(set(lineage_info["columns_used"]))
        
        return full_code, lineage_info
    
    def _generate_load_code(self, table_info: Dict) -> Tuple[str, Dict]:
        """Generate code to load normalized table"""
        file_path = table_info.get("file_path", "")
        sheet_name = table_info.get("sheet_name", "")
        
        # Check if it's a parquet file
        if file_path.endswith('.parquet'):
            code = f"""# Load normalized table (from parquet)
df = pd.read_parquet('{file_path}')
# Convert string columns back to appropriate types where possible
for col in df.columns:
    # Try to convert to numeric
    try:
        df[col] = pd.to_numeric(df[col], errors='ignore')
    except:
        pass
print(f"Loaded {{len(df)}} rows and {{len(df.columns)}} columns")
print("Columns:", list(df.columns))
print("\\nFirst few rows:")
print(df.head())
"""
        else:
            # Fallback to Excel
            code = f"""# Load normalized table
df = pd.read_excel('{file_path}', sheet_name='{sheet_name}', engine='openpyxl')
print(f"Loaded {{len(df)}} rows and {{len(df.columns)}} columns")
print("Columns:", list(df.columns))
print("\\nFirst few rows:")
print(df.head())
"""
        
        lineage = {
            "columns": list(table_info.get("columns", [])),
            "file_name": table_info.get("file_name", ""),
            "sheet_name": sheet_name
        }
        
        return code, lineage
    
    def _generate_filter_code(self, filters: List[Dict], column_mapping: Dict[str, str]) -> Tuple[str, Dict]:
        """Generate code for filtering"""
        code_parts = []
        columns_used = []
        
        for i, filter_cond in enumerate(filters):
            col = filter_cond.get("column", "")
            op = filter_cond.get("operator", "==")
            value = filter_cond.get("value", "")
            
            # Map column name
            mapped_col = column_mapping.get(col, col)
            columns_used.append(mapped_col)
            
            # Convert operator
            if op == "==":
                op_code = "=="
            elif op == "!=":
                op_code = "!="
            elif op == ">":
                op_code = ">"
            elif op == "<":
                op_code = "<"
            elif op == ">=":
                op_code = ">="
            elif op == "<=":
                op_code = "<="
            elif op == "in":
                op_code = ".isin"
            else:
                op_code = "=="
            
            # Generate filter condition
            if op_code == ".isin":
                code_parts.append(f"df = df[df['{mapped_col}'].isin({value})]")
            else:
                # Handle string values
                if isinstance(value, str):
                    value_str = f"'{value}'"
                else:
                    value_str = str(value)
                code_parts.append(f"df = df[df['{mapped_col}'] {op_code} {value_str}]")
        
        code = "# Apply filters\n" + "\n".join(code_parts)
        code += "\nprint(f\"After filtering: {len(df)} rows\")"
        
        return code, {"columns": columns_used}
    
    def _generate_aggregation_code(self, intent: Dict, column_mapping: Dict[str, str]) -> Tuple[str, Dict]:
        """Generate code for grouping and aggregation"""
        operations = intent.get("operations", [])
        group_by = intent.get("group_by", [])
        columns_used = []
        operations_used = []
        
        # Map group by columns
        group_by_cols = []
        for gb in group_by:
            mapped = column_mapping.get(f"group_by_{gb}", column_mapping.get(gb, gb))
            group_by_cols.append(mapped)
            columns_used.append(mapped)
        
        # Find metric column
        metric_col = column_mapping.get("metric", "")
        if not metric_col:
            # Try to infer from entities
            metric_col = column_mapping.get("sales", column_mapping.get("revenue", ""))
        
        # Generate aggregation code
        if group_by_cols:
            code = f"# Group by and aggregate\n"
            code += f"grouped = df.groupby({group_by_cols})\n"
            
            # If no metric column found, use first numeric column
            if not metric_col:
                code += "# Find first numeric column for aggregation\n"
                code += "numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()\n"
                code += "if len(numeric_cols) > 0:\n"
                code += "    metric_col = numeric_cols[0]\n"
                code += "else:\n"
                code += "    metric_col = None\n"
                code += "\n"
            
            agg_dict = {}
            for op in operations:
                op_name = op.lower()
                if metric_col:
                    if op_name in ["sum", "总和", "总计"]:
                        agg_dict[metric_col] = "sum"
                        operations_used.append("sum")
                    elif op_name in ["average", "avg", "mean", "平均"]:
                        agg_dict[metric_col] = "mean"
                        operations_used.append("average")
                    elif op_name in ["count", "数量", "个数"]:
                        agg_dict[metric_col] = "count"
                        operations_used.append("count")
                    elif op_name in ["min", "最小"]:
                        agg_dict[metric_col] = "min"
                        operations_used.append("min")
                    elif op_name in ["max", "最大"]:
                        agg_dict[metric_col] = "max"
                        operations_used.append("max")
            
            if agg_dict:
                code += f"if metric_col:\n"
                code += f"    result = grouped.agg({{metric_col: {list(agg_dict.values())[0]}}})\n"
                code += "else:\n"
                code += "    result = grouped.size().reset_index(name='count')\n"
                code += "result = result.reset_index()\n"
            else:
                code += "result = grouped.size().reset_index(name='count')\n"
                operations_used.append("count")
            
            if metric_col:
                columns_used.append(metric_col)
            
            code += "print('\\nAggregated results:')\n"
            code += "print(result)"
        else:
            # No grouping, just aggregate
            code = "# Aggregate\n"
            
            # If no metric column found, use first numeric column
            if not metric_col:
                code += "# Find first numeric column for aggregation\n"
                code += "numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()\n"
                code += "if len(numeric_cols) > 0:\n"
                code += "    metric_col = numeric_cols[0]\n"
                code += "else:\n"
                code += "    metric_col = None\n"
                code += "\n"
            
            agg_code_parts = []
            for op in operations:
                op_name = op.lower()
                if metric_col:
                    if op_name in ["sum", "总和", "总计"]:
                        agg_code_parts.append(f"result = df['{metric_col}'].sum()")
                        operations_used.append("sum")
                    elif op_name in ["average", "avg", "mean", "平均"]:
                        agg_code_parts.append(f"result = df['{metric_col}'].mean()")
                        operations_used.append("average")
                    elif op_name in ["count", "数量", "个数"]:
                        agg_code_parts.append(f"result = len(df)")
                        operations_used.append("count")
            
            if agg_code_parts:
                code += agg_code_parts[0] + "\n"
            elif metric_col:
                code += f"result = df['{metric_col}'].sum()\n"
                operations_used.append("sum")
            else:
                code += "result = len(df)\n"
                operations_used.append("count")
            
            code += "print(f'Result: {result}')"
            if metric_col:
                columns_used.append(metric_col)
        
        return code, {"columns": columns_used, "operations": operations_used}
    
    def _generate_sort_code(self, sort_config: Dict, column_mapping: Dict[str, str]) -> Tuple[str, Dict]:
        """Generate code for sorting"""
        col = sort_config.get("column", "")
        ascending = sort_config.get("ascending", True)
        limit = sort_config.get("limit", None)
        
        mapped_col = column_mapping.get(col, col)
        
        code = f"# Sort\n"
        code += f"result = result.sort_values('{mapped_col}', ascending={ascending})\n"
        
        if limit:
            code += f"result = result.head({limit})\n"
        
        code += "print('\\nSorted results:')\n"
        code += "print(result)"
        
        return code, {"columns": [mapped_col]}
    
    def _generate_visualization_code(self, intent: Dict, column_mapping: Dict[str, str]) -> Tuple[str, Dict]:
        """Generate code for visualization"""
        code = "# Create visualization\n"
        
        # Determine chart type based on intent
        if intent.get("intent_type") == "trend":
            # Time series plot
            date_col = column_mapping.get("date", "")
            metric_col = column_mapping.get("metric", "")
            code += f"fig = px.line(result, x='{date_col}', y='{metric_col}', title='Trend Analysis')\n"
        elif intent.get("group_by"):
            # Grouped bar chart
            group_col = column_mapping.get(f"group_by_{intent['group_by'][0]}", "")
            metric_col = column_mapping.get("metric", "")
            code += f"fig = px.bar(result, x='{group_col}', y='{metric_col}', title='Grouped Analysis')\n"
        else:
            # Default bar chart
            metric_col = column_mapping.get("metric", "")
            code += f"fig = px.bar(result, y='{metric_col}', title='Analysis Results')\n"
        
        code += "fig.show()\n"
        code += "# Save plot\n"
        code += "fig.write_html('analysis_result.html')\n"
        code += "print('Visualization saved to analysis_result.html')"
        
        columns_used = list(column_mapping.values())
        return code, {"columns": columns_used}
    
    def _generate_display_code(self, intent: Dict) -> str:
        """Generate code to display results"""
        code = "# Display final results\n"
        code += "print('\\n' + '='*50)\n"
        code += "print('FINAL RESULTS')\n"
        code += "print('='*50)\n"
        # Check if result variable exists, otherwise use df
        code += "if 'result' in locals():\n"
        code += "    print(result)\n"
        code += "else:\n"
        code += "    print('Data loaded successfully!')\n"
        code += "    print(f'Total rows: {len(df)}')\n"
        code += "    print('\\nData preview:')\n"
        code += "    print(df.head(10))\n"
        code += "print('\\n' + '='*50)"
        return code

