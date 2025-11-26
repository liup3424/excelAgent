"""
Safely execute generated Python code
"""

import sys
import io
import traceback
from typing import Dict, Optional, Any, List
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


class CodeExecutor:
    """Safely executes generated Python code"""
    
    def __init__(self):
        """Initialize executor"""
        self.allowed_modules = {
            'pandas', 'pd', 'numpy', 'np', 
            'matplotlib', 'plt', 'plotly', 'px', 'go'
        }
        self.execution_globals = {
            'pd': pd,
            'np': np,
            'plt': plt,
            'px': px,
            'go': go,
            '__builtins__': __builtins__
        }
    
    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code safely
        
        Args:
            code: Python code to execute
        
        Returns:
            Dictionary with:
            - success: bool
            - output: str (stdout)
            - error: str (if failed)
            - result: Any (result object if available)
        """
        # Capture stdout
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        try:
            # Execute code
            exec(code, self.execution_globals)
            
            # Get output
            output = captured_output.getvalue()
            
            # Try to get result variable
            result = self.execution_globals.get('result', None)
            
            return {
                "success": True,
                "output": output,
                "error": None,
                "result": result
            }
        
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return {
                "success": False,
                "output": captured_output.getvalue(),
                "error": error_msg,
                "result": None
            }
        
        finally:
            sys.stdout = old_stdout
    
    def execute_with_error_handling(self, code: str, column_mapping: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute code with enhanced error handling and suggestions
        
        Args:
            code: Python code to execute
            column_mapping: Column mapping for error suggestions
        
        Returns:
            Execution result with suggestions
        """
        result = self.execute_code(code)
        
        if not result["success"]:
            # Try to provide helpful suggestions
            error = result["error"]
            suggestions = self._generate_suggestions(error, column_mapping)
            result["suggestions"] = suggestions
        
        return result
    
    def _generate_suggestions(self, error: str, column_mapping: Dict[str, str]) -> List[str]:
        """Generate helpful suggestions based on error"""
        suggestions = []
        
        # Check for KeyError (missing column)
        if "KeyError" in error or "not found" in error.lower():
            suggestions.append("Column not found. Available columns:")
            suggestions.append(f"  {list(column_mapping.values())}")
            suggestions.append("Consider checking column names for typos or case sensitivity.")
        
        # Check for type errors
        if "TypeError" in error:
            suggestions.append("Type error detected. Check data types:")
            suggestions.append("  - Use df.dtypes to check column types")
            suggestions.append("  - Convert types if needed: pd.to_numeric(), pd.to_datetime()")
        
        # Check for empty results
        if "empty" in error.lower():
            suggestions.append("No data matches the filters. Try:")
            suggestions.append("  - Relaxing filter conditions")
            suggestions.append("  - Checking filter values")
        
        return suggestions

