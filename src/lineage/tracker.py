"""
Track data lineage - which Excel columns were used
"""

from typing import Dict, List, Optional


class LineageTracker:
    """Tracks which columns were used in analysis"""
    
    def __init__(self):
        """Initialize lineage tracker"""
        pass
    
    def create_lineage_report(
        self, 
        lineage_info: Dict,
        execution_result: Dict
    ) -> Dict:
        """
        Create a comprehensive lineage report
        
        Args:
            lineage_info: Metadata from code generation
            execution_result: Result from code execution
        
        Returns:
            Lineage report dictionary
        """
        report = {
            "file_name": lineage_info.get("file_name", "Unknown"),
            "sheet_name": lineage_info.get("sheet_name", "Unknown"),
            "columns_used": lineage_info.get("columns_used", []),
            "operations": lineage_info.get("operations", []),
            "success": execution_result.get("success", False)
        }
        
        # Add human-readable explanation
        report["explanation"] = self._generate_explanation(report)
        
        return report
    
    def _generate_explanation(self, report: Dict) -> str:
        """Generate human-readable explanation"""
        parts = []
        
        parts.append(f"This analysis used data from:")
        parts.append(f"  - File: {report['file_name']}")
        parts.append(f"  - Sheet: {report['sheet_name']}")
        parts.append("")
        
        if report["columns_used"]:
            parts.append("Columns used:")
            for col in report["columns_used"]:
                parts.append(f"  - {col}")
            parts.append("")
        
        if report["operations"]:
            parts.append("Operations performed:")
            for op in report["operations"]:
                parts.append(f"  - {op}")
            parts.append("")
        
        return "\n".join(parts)
    
    def format_lineage_for_display(self, report: Dict) -> str:
        """Format lineage report for user display"""
        return report.get("explanation", "")

