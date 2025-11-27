"""
Generate Python code for data analysis using LLM
"""

from typing import Dict, List, Optional, Tuple
import json
import os
from dotenv import load_dotenv

load_dotenv()


class CodeGenerator:
    """Generates Python code for analysis using LLM"""
    
    def __init__(self, llm_client=None):
        """
        Initialize code generator
        
        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.). If None, uses OpenAI.
        """
        self.llm_client = llm_client
        self._init_llm_client()
        self.use_llm = self.llm_client is not None
    
    def _init_llm_client(self):
        """Initialize LLM client"""
        if self.llm_client is not None:
            return
        
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.llm_client = OpenAI(api_key=api_key)
            else:
                self.llm_client = None
        except ImportError:
            self.llm_client = None
    
    def generate_code(
        self, 
        intent: Dict, 
        column_mapping: Dict[str, str],
        table_info: Dict,
        question: str
    ) -> Tuple[str, Dict]:
        """
        Generate Python code for analysis using LLM
        
        Args:
            intent: Extracted intent
            column_mapping: Mapping of entities to columns
            table_info: Information about the table to analyze
            question: Original user question
        
        Returns:
            Tuple of (generated code, metadata about columns used)
        """
        if not self.use_llm:
            raise ValueError(
                "LLM code generation requires OPENAI_API_KEY. "
                "Please set OPENAI_API_KEY in your .env file."
            )
        
        try:
            code, lineage_info = self._generate_code_with_llm(
                intent, column_mapping, table_info, question
            )
            if not code:
                raise ValueError("LLM failed to generate code. Please check your API key and try again.")
            return code, lineage_info
        except Exception as e:
            print(f"LLM code generation failed: {e}")
            raise
    
    def _generate_code_with_llm(
        self,
        intent: Dict,
        column_mapping: Dict[str, str],
        table_info: Dict,
        question: str
    ) -> Tuple[str, Dict]:
        """Generate code using LLM"""
        # Build context information
        context = self._build_context(intent, column_mapping, table_info, question)
        
        # Generate prompt
        prompt = self._build_code_generation_prompt(context, question)
        
        # Call LLM
        code = self._call_llm_for_code(prompt)
        
        if not code:
            return "", {}
        
        # Extract lineage info - try to infer from code and context
        columns_used = self._extract_columns_from_code(code, table_info.get("columns", []))
        
        lineage_info = {
            "columns_used": columns_used if columns_used else list(table_info.get("columns", [])),
            "operations": intent.get("operations", []),
            "file_name": table_info.get("file_name", ""),
            "sheet_name": table_info.get("sheet_name", "")
        }
        
        return code, lineage_info
    
    def _extract_columns_from_code(self, code: str, available_columns: List[str]) -> List[str]:
        """Extract column names used in the generated code"""
        import re
        columns_used = []
        
        # Look for column references in code (df['column'], df.column, etc.)
        patterns = [
            r"df\['([^']+)'\]",  # df['column']
            r'df\["([^"]+)"\]',  # df["column"]
            r"df\.([a-zA-Z_][a-zA-Z0-9_]*)",  # df.column
            r"groupby\(['\"]([^'\"]+)['\"]",  # groupby('column')
            r"sort_values\(['\"]([^'\"]+)['\"]",  # sort_values('column')
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, code)
            for match in matches:
                if match in available_columns and match not in columns_used:
                    columns_used.append(match)
        
        return columns_used
    
    def _build_context(
        self,
        intent: Dict,
        column_mapping: Dict[str, str],
        table_info: Dict,
        question: str
    ) -> Dict:
        """Build context information for LLM"""
        return {
            "file_path": table_info.get("file_path", ""),
            "file_name": table_info.get("file_name", ""),
            "sheet_name": table_info.get("sheet_name", ""),
            "columns": table_info.get("columns", []),
            "column_types": table_info.get("column_types", {}),
            "row_count": table_info.get("row_count", 0),
            "intent": intent,
            "column_mapping": column_mapping,
            "question": question
        }
    
    def _build_code_generation_prompt(self, context: Dict, question: str) -> str:
        """Build comprehensive prompt for code generation"""
        
        file_path = context["file_path"]
        columns = context["columns"]
        column_types = context.get("column_types", {})
        intent = context["intent"]
        column_mapping = context["column_mapping"]
        
        # Build column information
        column_info = []
        for col in columns:
            col_type = column_types.get(col, "unknown")
            column_info.append(f"  - {col} ({col_type})")
        columns_str = "\n".join(column_info) if column_info else "  (No columns available)"
        
        # Build intent information
        intent_info = f"""
Intent Type: {intent.get('intent_type', 'unknown')}
Operations: {', '.join(intent.get('operations', []))}
Group By: {', '.join(intent.get('group_by', []))}
Filters: {len(intent.get('filters', []))} filter(s)
Sort: {intent.get('sort', 'None')}
"""
        
        # Build column mapping information
        mapping_list = []
        for entity, col in column_mapping.items():
            mapping_list.append(f"  - {entity} → {col}")
        mapping_str = "\n".join(mapping_list) if mapping_list else "  (No mappings)"
        
        prompt = f"""You are an expert Python data analyst specializing in Excel data processing with pandas.

**Task**: Generate Python code to answer the user's question about Excel data.

**Excel File Information**:
- File Path: {file_path}
- Sheet Name: {context['sheet_name']}
- Total Rows: {context['row_count']}
- Columns ({len(columns)}):
{columns_str}

**User Question**: {question}

**Analysis Intent**:
{intent_info}

**Column Mappings**:
{mapping_str}

**Additional Context**:
- File contains {context['row_count']} rows
- Column types: {', '.join(set(column_types.values())) if column_types else 'unknown'}

**IMPORTANT - Result Variable Requirement**:
- You MUST assign the final analysis result to a variable named "result"
- If user asks to "show table", "display data", "return results", etc., assign the DataFrame to: result = <dataframe>
- If user asks for calculations/aggregations, assign the result to: result = <calculation_result>
- If user asks for visualizations, ALSO assign the underlying data to: result = <dataframe>
- The "result" variable is automatically captured and displayed in the UI tables
- Without assigning to "result", the UI will show empty tables

**Excel Data Processing Rules**

1. **Basic Code Structure Requirements**:

    1.1 **Required Imports and Settings**:
```python
import pandas as pd
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=Warning)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
import plotly.express as px
import plotly.graph_objects as go
```

    1.2 **Output Format Requirements**:
        - Output ONLY the code, no additional explanations
        - Do NOT include any Markdown or code block markers (no ```python or ```)
        - Output pure Python code as plain text
        - All results must be printed to console using "print()"

2. **Data Query and Processing Requirements**:

    2.1 **Multi-row Data Processing**:
        - Before generating code, determine if the user wants data "within a range" or "a specific value"
        - When sorting results, explicitly specify `ascending=False` (descending) or `True` (ascending)
        - Avoid relying on default sorting behavior

    2.2 **Key Field Processing**:
        - Time fields MUST be converted using `pd.to_datetime(..., errors='coerce').dt.normalize()` and extract year/month/day components for comparison
        - For identifier fields, use `.astype(str)` to convert to string type to avoid unexpected format changes (leading zeros, scientific notation, precision truncation)
        - Numeric fields MUST be converted using `pd.to_numeric(..., errors='coerce')` to avoid string comparison with numbers
        - To ensure numerical calculations (sum, comparison, aggregation, sorting), convert data to numeric type using "pd.to_numeric(data, errors='coerce')" before calculation, ignoring values that cannot be converted

    2.3 **Data Cleaning and Processing**:
        - The "DataFrame.fillna" method with "method" parameter is deprecated
        - Keep special characters in column names (underscores, multiple spaces, etc.) unchanged

    2.4 **Output Specification**:
        - When outputting in batches, format and print line by line

3. **Code Robustness Requirements**:

    3.1 **Exception Handling**:
        - Code MUST include exception handling mechanism
        - Wrap file operations and data processing logic with try-except
        - Catch common exceptions like FileNotFoundError, KeyError and provide friendly messages
        - When printing exceptions, include specific error information: print(f"Error details: {{str(e)}}")

    3.2 **Data Validation**:
        - Check df.empty immediately after reading data to avoid operating on empty DataFrame
        - For key filter fields (like "customer_name"), first confirm existence using df.columns
        - If file has multiple sheets, generate code for each qualifying sheet

4. **Naming Conventions**:

    4.1 **Variable and Function Naming**:
        - Avoid using symbols like # in function or variable names (it's a comment symbol)
        - Avoid using Chinese characters in function or variable names
        - Use meaningful English variable names, such as filtered_df, result_data, etc.

5. **Problem Decomposition Principles**:

    5.1 **Analyze User Requirements**:
        - First parse key dimensions of user's question
        - Convert natural language descriptions into corresponding pandas operation chains

    5.2 **Defensive Programming**:
        - Assume raw data may have missing values, type confusion, or special characters

6. **Visualization Requirements**:
    - If the user's question requires creating a chart, use "import plotly.graph_objects as go" to generate an interactive local HTML page
    - Page name must be "workspace/charts/analysis_result.html" (create directory if needed)
    - For go.Figure, set mode parameter to "lines+markers+text" when appropriate
    - fig.update_layout must include title (centered), xaxis_title, yaxis_title
    - X-axis data must be sorted from small to large before plotting
    - Also save as PNG: fig.write_image("workspace/charts/analysis_result.png")

**Instructions**:
1. Load the data from: {file_path}
   - Use pd.read_parquet() if file ends with .parquet
   - Use pd.read_excel() with engine='openpyxl' otherwise
   - Wrap file loading in try-except block
2. Answer the user's question: "{question}"
3. Generate complete, executable Python code following all the rules above
4. Include proper error handling with try-except blocks for all operations
5. Validate data (check df.empty immediately after loading, verify columns exist before use)
6. **CRITICAL: Always assign the final result to a variable named "result"**
   - If the user asks to show/display/return a table or data, assign the DataFrame to: result = <your_dataframe>
   - If the user asks for aggregation/calculation, assign the result to: result = <your_calculation>
   - If the user asks for filtered/sorted data, assign the final DataFrame to: result = <your_dataframe>
   - The "result" variable will be automatically captured and displayed in the UI
7. Print all results to console using print() statements
8. If visualization is needed (user asks for charts/plots/graphs):
   - Create "workspace/charts/" directory if it doesn't exist: os.makedirs("workspace/charts", exist_ok=True)
   - Save to "workspace/charts/analysis_result.html" using plotly: fig.write_html("workspace/charts/analysis_result.html")
   - Optionally save as PNG (wrap in try-except):
     * try:
     *     fig.write_image("workspace/charts/analysis_result.png")
     *     print("Chart saved as PNG")
     * except Exception as e:
     *     print(f"Could not save PNG (kaleido may not be installed): {{str(e)}}")
   - Make sure to import os: import os
   - If the chart is based on a DataFrame, also assign that DataFrame to result: result = <your_dataframe>
9. Handle data types properly:
   - Convert dates: pd.to_datetime(..., errors='coerce').dt.normalize()
   - Convert numeric: pd.to_numeric(..., errors='coerce')
   - Convert identifiers: .astype(str)

**Important**: 
- Output ONLY the Python code
- Do NOT include markdown code blocks (no ```python or ```)
- Do NOT include explanations or comments outside the code
- Code must be directly executable
- All code must be inside try-except blocks for robustness

**Generate the Python code now**:"""

        return prompt
    
    def _call_llm_for_code(self, prompt: str) -> str:
        """Call LLM to generate code"""
        if self.llm_client is None:
            return ""
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4" for better quality
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert Python data analyst specializing in pandas and Excel data processing. 
Your task is to generate clean, executable Python code that:
1. Follows all the rules and requirements provided
2. Includes proper error handling
3. Validates data before processing
4. Handles data types correctly
5. Outputs ONLY the Python code (no markdown, no explanations, no code blocks)
6. Is directly executable"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=3000  # Increased for more complex code
            )
            
            code = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            lines = code.split('\n')
            # Remove first line if it's a code block marker
            if lines and (lines[0].startswith("```python") or lines[0].startswith("```")):
                lines = lines[1:]
            # Remove last line if it's a code block marker
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            
            code = '\n'.join(lines).strip()
            
            return code
        
        except Exception as e:
            print(f"Error calling LLM for code generation: {e}")
            import traceback
            traceback.print_exc()
            return ""

