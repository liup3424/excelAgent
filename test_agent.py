#!/usr/bin/env python3
"""
Quick test script for the Excel Analysis Agent
"""

import sys
from src.agent import ExcelAnalysisAgent

def test_agent():
    """Test agent initialization and basic functionality"""
    print("="*60)
    print("Testing Excel Analysis Agent")
    print("="*60)
    
    try:
        print("\n1. Initializing agent...")
        # Initialize without excel_dir since files are uploaded via UI
        agent = ExcelAnalysisAgent(excel_dir=None)
        print(f"   ✓ Agent initialized successfully!")
        print(f"   ✓ Found {len(agent.normalized_tables)} normalized tables")
        
        if len(agent.normalized_tables) == 0:
            print("   ℹ No tables loaded. Upload Excel files via Gradio UI to start analyzing.")
            return True
        
        if agent.normalized_tables:
            print("\n2. Available tables:")
            for i, table in enumerate(agent.normalized_tables, 1):
                print(f"   {i}. {table['name']}")
                print(f"      File: {table['file_name']}")
                print(f"      Sheet: {table['sheet_name']}")
                print(f"      Columns: {len(table['columns'])} columns")
                print(f"      Rows: {table['row_count']} rows")
        
        print("\n3. Testing a simple query...")
        test_question = "列出所有表格"
        print(f"   Question: {test_question}")
        result = agent.analyze(test_question)
        
        if result["success"]:
            print("   ✓ Analysis completed successfully!")
        else:
            print(f"   ⚠ Analysis completed with issues: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*60)
        print("Test completed!")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)

