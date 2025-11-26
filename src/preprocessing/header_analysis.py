"""
LLM-based header classification (labels vs headers)
"""

import json
from typing import Dict, List, Optional
import pandas as pd
from openpyxl import load_workbook


class HeaderAnalyzer:
    """Uses LLM to classify rows as labels or headers"""
    
    def __init__(self, llm_client=None):
        """
        Initialize header analyzer
        
        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.). If None, uses OpenAI.
        """
        self.llm_client = llm_client
        self._init_llm_client()
    
    def _init_llm_client(self):
        """Initialize LLM client"""
        try:
            from openai import OpenAI
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.llm_client = OpenAI(api_key=api_key)
            else:
                print("Warning: OPENAI_API_KEY not found. Using mock mode.")
                self.llm_client = None
        except ImportError:
            print("Warning: openai not installed. Using mock mode.")
            self.llm_client = None
    
    def _format_sample_for_llm(self, sample_df: pd.DataFrame) -> str:
        """
        Format sample DataFrame for LLM input
        
        Args:
            sample_df: Sample rows DataFrame
        
        Returns:
            Formatted string representation
        """
        # Convert to string representation
        # Replace NaN with empty string for cleaner output
        df_str = sample_df.fillna('').to_string(index=True)
        return df_str
    
    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM with prompt
        
        Args:
            prompt: Prompt string
        
        Returns:
            LLM response
        """
        if self.llm_client is None:
            # Mock response for testing
            return self._mock_llm_response()
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",  # or "gpt-4" for better accuracy
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing Excel spreadsheet structures. Your task is to classify rows as either 'labels' (descriptive text to remove) or 'header' (table headers to keep and merge)."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return self._mock_llm_response()
    
    def _mock_llm_response(self) -> str:
        """Mock LLM response for testing"""
        # Simple heuristic: assume first 1-2 rows might be labels, next 1-3 rows are headers
        return json.dumps({
            "labels": [1, 2],
            "header": [3, 4]
        })
    
    def analyze_headers(self, sample_df: pd.DataFrame, sheet_name: str) -> Dict[str, List[int]]:
        """
        Analyze sample rows to classify as labels or headers
        
        Args:
            sample_df: Sample rows DataFrame (top N rows)
            sheet_name: Name of the sheet
        
        Returns:
            Dictionary with 'labels' and 'header' keys, each containing list of row indices (1-based)
        """
        # Format sample for LLM
        sample_str = self._format_sample_for_llm(sample_df)
        
        # Create prompt
        prompt = f"""Analyze the following Excel sheet sample rows and classify each row as either:
1. "labels" - descriptive text, titles, notes, or explanatory rows that should be removed
2. "header" - rows that are part of the table header structure (may be multi-level)

Sheet name: {sheet_name}

Sample rows (row numbers shown on left):
{sample_str}

Return a JSON object with this structure:
{{
  "labels": [list of 1-based row indices that are descriptive labels to remove],
  "header": [list of 1-based row indices that form the table header]
}}

Rules:
- Row indices should be 1-based (first row is 1, not 0)
- If there are no label rows, use empty list: "labels": []
- Header rows should include all rows that form the table structure (can be multi-level)
- Data rows should NOT be included in either list

Return only valid JSON, no additional text."""

        # Call LLM
        response = self._call_llm(prompt)
        
        # Parse response
        try:
            result = json.loads(response)
            # Validate structure
            if "labels" not in result or "header" not in result:
                raise ValueError("Invalid response structure")
            
            # Ensure lists are sorted
            result["labels"] = sorted(result.get("labels", []))
            result["header"] = sorted(result.get("header", []))
            
            return result
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response was: {response}")
            # Fallback to mock response
            return self._mock_llm_response_parsed()
    
    def _mock_llm_response_parsed(self) -> Dict[str, List[int]]:
        """Parsed mock response"""
        return {
            "labels": [1, 2],
            "header": [3, 4]
        }

