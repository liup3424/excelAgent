"""
Main entry point for Excel Analysis Agent
"""

import argparse
import asyncio
from src.agent import ExcelAnalysisAgent
from src.websocket import WebSocketServer


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Excel Analysis Agent")
    parser.add_argument(
        "--mode",
        choices=["cli", "websocket"],
        default="cli",
        help="Run mode: cli (command line) or websocket (WebSocket server)"
    )
    parser.add_argument(
        "--excel-dir",
        default=None,
        help="Directory containing Excel files (optional, files can be uploaded via UI)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="WebSocket server host (for websocket mode)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="WebSocket server port (for websocket mode)"
    )
    
    args = parser.parse_args()
    
    # Initialize agent
    print("Initializing Excel Analysis Agent...")
    agent = ExcelAnalysisAgent(excel_dir=args.excel_dir)
    
    if args.mode == "cli":
        # Command line mode
        print("\n" + "="*60)
        print("Excel Analysis Agent - CLI Mode")
        print("="*60)
        print("Enter your questions (or 'quit' to exit)")
        print("="*60 + "\n")
        
        while True:
            try:
                question = input("Question: ").strip()
                
                if question.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                
                if not question:
                    continue
                
                result = agent.analyze(question)
                
                # Display results
                print("\n" + "="*60)
                print("RESULTS")
                print("="*60)
                
                if result["success"]:
                    print("\n✓ Analysis completed successfully!")
                else:
                    print("\n✗ Analysis failed!")
                    if result.get("error"):
                        print(f"Error: {result['error']}")
                
                print("\n" + "="*60 + "\n")
            
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                import traceback
                traceback.print_exc()
    
    elif args.mode == "websocket":
        # WebSocket mode
        print(f"\nStarting WebSocket server on {args.host}:{args.port}")
        server = WebSocketServer(analysis_agent=agent)
        server.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()

