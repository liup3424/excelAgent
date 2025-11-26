"""
Extract analysis intent from natural language questions
"""

import json
from typing import Dict, List, Optional
import re


class IntentExtractor:
    """Extracts analysis intent from user questions"""
    
    def __init__(self, llm_client=None):
        """
        Initialize intent extractor
        
        Args:
            llm_client: LLM client (OpenAI, Anthropic, etc.)
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
    
    def extract_intent(self, question: str, available_tables: List[Dict]) -> Dict:
        """
        Extract analysis intent from question
        
        Args:
            question: User's natural language question
            available_tables: List of available normalized tables with metadata
        
        Returns:
            Dictionary containing:
            - intent_type: aggregation, grouping, trend, filter, sort, comparison
            - operations: list of operations (sum, avg, count, etc.)
            - group_by: columns to group by
            - filters: filter conditions
            - sort: sort configuration
            - entities: extracted entities (region, sales, date, etc.)
            - selected_tables: relevant tables to use
        """
        # Format available tables info for LLM
        tables_info = self._format_tables_info(available_tables)
        
        # Create prompt
        prompt = f"""Analyze the following user question and extract the analysis intent.

User question: {question}

Available tables:
{tables_info}

Extract the following information:
1. Intent type: one of [aggregation, grouping, trend, filter, sort, comparison, visualization]
2. Operations: list of aggregation operations needed (sum, average, count, min, max, etc.)
3. Group by: columns to group by (if any)
4. Filters: filter conditions (column, operator, value)
5. Sort: sort configuration (column, ascending/descending, limit)
6. Entities: extracted entities from the question (e.g., "地区" -> region, "销售额" -> sales)
7. Selected tables: which table(s) from the available tables should be used

Return a JSON object with this structure:
{{
  "intent_type": "aggregation|grouping|trend|filter|sort|comparison|visualization",
  "operations": ["sum", "average", ...],
  "group_by": ["column1", "column2", ...],
  "filters": [
    {{"column": "col_name", "operator": "==", "value": "value"}},
    ...
  ],
  "sort": {{"column": "col_name", "ascending": false, "limit": 10}},
  "entities": {{
    "region": ["地区", "区域"],
    "sales": ["销售额", "sales"],
    "date": ["日期", "date"]
  }},
  "selected_tables": ["table1", "table2"]
}}

If a field is not applicable, use null or empty list/object."""

        # Call LLM
        response = self._call_llm(prompt)
        
        # Parse response
        try:
            intent = json.loads(response)
            return self._validate_intent(intent)
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response: {e}")
            return self._fallback_intent_extraction(question)
    
    def _format_tables_info(self, tables: List[Dict]) -> str:
        """Format table metadata for LLM"""
        info_lines = []
        for i, table in enumerate(tables):
            info_lines.append(f"Table {i+1}: {table.get('name', 'Unknown')}")
            info_lines.append(f"  File: {table.get('file_name', 'Unknown')}")
            info_lines.append(f"  Sheet: {table.get('sheet_name', 'Unknown')}")
            info_lines.append(f"  Columns: {', '.join(table.get('columns', []))}")
            info_lines.append("")
        return "\n".join(info_lines)
    
    def _call_llm(self, prompt: str) -> str:
        """Call LLM with prompt"""
        if self.llm_client is None:
            return self._mock_llm_response()
        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing data analysis requests. Extract structured intent from natural language questions."
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
        """Mock LLM response"""
        return json.dumps({
            "intent_type": "grouping",
            "operations": ["sum"],
            "group_by": ["region"],
            "filters": [],
            "sort": None,
            "entities": {"region": ["地区"], "sales": ["销售额"]},
            "selected_tables": []
        })
    
    def _validate_intent(self, intent: Dict) -> Dict:
        """Validate and normalize intent structure"""
        # Ensure all required fields exist
        default_intent = {
            "intent_type": "aggregation",
            "operations": [],
            "group_by": [],
            "filters": [],
            "sort": None,
            "entities": {},
            "selected_tables": []
        }
        
        # Merge with defaults
        validated = {**default_intent, **intent}
        
        return validated
    
    def _fallback_intent_extraction(self, question: str) -> Dict:
        """Fallback rule-based intent extraction"""
        question_lower = question.lower()
        
        intent_type = "aggregation"
        operations = []
        group_by = []
        
        # Detect operations
        if any(word in question_lower for word in ["总和", "总计", "sum", "total"]):
            operations.append("sum")
        if any(word in question_lower for word in ["平均", "average", "avg", "mean"]):
            operations.append("average")
        if any(word in question_lower for word in ["数量", "count", "个数"]):
            operations.append("count")
        
        # Detect grouping
        if any(word in question_lower for word in ["按", "by", "group", "分组"]):
            # Try to extract group by column
            if "地区" in question or "region" in question_lower:
                group_by.append("region")
            if "产品" in question or "product" in question_lower:
                group_by.append("product")
        
        # Detect sorting
        sort_config = None
        if any(word in question_lower for word in ["top", "前", "最大", "最高"]):
            sort_config = {"ascending": False, "limit": 10}
        elif any(word in question_lower for word in ["bottom", "后", "最小", "最低"]):
            sort_config = {"ascending": True, "limit": 10}
        
        return {
            "intent_type": intent_type,
            "operations": operations if operations else ["sum"],
            "group_by": group_by,
            "filters": [],
            "sort": sort_config,
            "entities": {},
            "selected_tables": []
        }

