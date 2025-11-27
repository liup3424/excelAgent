"""
Backend API functions for Gradio UI
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from .utils.data_manager import DataManager
from .utils.file_manager import FileManager
from .preprocessing import UnmergeProcessor, HeaderAnalyzer, TableNormalizer
from .nlp import IntentExtractor, ColumnMapper
from .codegen import CodeGenerator, CodeExecutor
from .lineage import LineageTracker


def upload_excels(files: List) -> Dict:
    """
    Upload and preprocess Excel files
    
    Args:
        files: List of uploaded file paths (from Gradio File component)
    
    Returns:
        Dictionary with upload status and table information
    """
    data_manager = DataManager()
    data_manager.initialize_directories()
    
    # Clear existing tables and files before uploading new ones
    data_manager.clear_tables()
    
    if not files:
        return {
            "status": "error",
            "message": "No files provided",
            "num_files": 0,
            "tables": []
        }
    
    # Process each file
    processed_files = []
    unmerge_processor = None
    header_analyzer = HeaderAnalyzer()
    table_normalizer = TableNormalizer()
    
    for file_path in files:
        try:
            # Copy file to workspace/uploads
            file_name = Path(file_path).name
            dest_path = data_manager.uploads_dir / file_name
            
            # Always copy (overwrite if exists) since we cleared everything
            shutil.copy2(file_path, dest_path)
            
            # Get file info
            file_manager = FileManager(str(data_manager.uploads_dir))
            sheets = file_manager.get_sheet_names(dest_path)
            
            file_tables = []
            
            for sheet_name in sheets:
                try:
                    # Step 1: Unmerge cells
                    unmerge_processor = UnmergeProcessor(str(dest_path))
                    df_unmerged = unmerge_processor.process_sheet(sheet_name)
                    
                    # Step 2: Get sample rows for header analysis
                    sample_df = unmerge_processor.get_sample_rows(df_unmerged, n=10)
                    
                    # Step 3: Classify rows (labels vs headers)
                    classification = header_analyzer.analyze_headers(sample_df, sheet_name)
                    
                    # Step 4: Normalize table
                    normalized_df, metadata = table_normalizer.normalize_table(
                        df_unmerged,
                        classification
                    )
                    
                    # Step 5: Save normalized table
                    table_name = f"{dest_path.stem}_{sheet_name}"
                    table_path = data_manager.workspace_dir / "data" / f"{table_name}.parquet"
                    table_path.parent.mkdir(exist_ok=True, parents=True)
                    
                    # Convert to string to avoid parquet type issues
                    normalized_df_str = normalized_df.astype(str).replace('nan', '')
                    normalized_df_str.to_parquet(table_path, index=False)
                    
                    # Store metadata
                    table_info = {
                        "name": table_name,
                        "file_path": str(table_path),
                        "file_name": file_name,
                        "sheet_name": sheet_name,
                        "columns": list(normalized_df.columns),
                        "column_types": metadata.get("column_types", {}),
                        "row_count": len(normalized_df),
                        "metadata": metadata
                    }
                    
                    data_manager.add_table(table_info)
                    file_tables.append({
                        "sheet": sheet_name,
                        "rows": len(normalized_df),
                        "columns": len(normalized_df.columns)
                    })
                
                except Exception as e:
                    print(f"Error processing sheet {sheet_name}: {e}")
                    continue
            
            processed_files.append({
                "file": file_name,
                "sheets": file_tables
            })
        
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue
    
    return {
        "status": "ok",
        "num_files": len(processed_files),
        "tables": processed_files,
        "total_tables": len(data_manager.get_tables())
    }


def run_query(question: str, language: str = "auto") -> Dict:
    """
    Run analysis query on uploaded Excel files
    
    Args:
        question: Natural language question
        language: Language code ("auto", "zh", "en")
    
    Returns:
        Dictionary with code, results, and lineage
    """
    data_manager = DataManager()
    tables = data_manager.get_tables()
    
    if not tables:
        return {
            "status": "error",
            "message": "No Excel files uploaded. Please upload files first.",
            "code": "",
            "results": {},
            "lineage": {}
        }
    
    if not question or not question.strip():
        return {
            "status": "error",
            "message": "Please provide a question.",
            "code": "",
            "results": {},
            "lineage": {}
        }
    
    try:
        # Initialize components
        intent_extractor = IntentExtractor()
        column_mapper = ColumnMapper()
        code_generator = CodeGenerator(llm_client=None)  # Will auto-initialize OpenAI if API key available
        code_executor = CodeExecutor()
        lineage_tracker = LineageTracker()
        
        # Step 1: Extract intent
        intent = intent_extractor.extract_intent(question, tables)
        
        # Step 2: Map entities to columns
        entity_mapping = column_mapper.map_entities_to_columns(
            intent.get("entities", {}),
            tables,
            intent
        )
        
        # Infer additional columns from intent
        inferred_mapping = column_mapper.infer_columns_from_intent(intent, tables)
        column_mapping = {**entity_mapping, **inferred_mapping}
        
        # Step 3: Select table
        selected_table = None
        selected_tables = intent.get("selected_tables", [])
        
        if selected_tables:
            selected_table = data_manager.get_table_by_name(selected_tables[0])
        
        if not selected_table and tables:
            selected_table = tables[0]
        
        if not selected_table:
            return {
                "status": "error",
                "message": "No suitable table found for analysis",
                "code": "",
                "results": {},
                "lineage": {}
            }
        
        # Step 4: Generate code
        code, lineage_info = code_generator.generate_code(
            intent,
            column_mapping,
            selected_table,
            question
        )
        
        # Step 5: Execute code
        execution_result = code_executor.execute_with_error_handling(
            code,
            column_mapping
        )
        
        # Step 6: Process results
        results = {
            "tables": [],
            "charts": [],
            "summary": ""
        }
        
        if execution_result["success"]:
            # Extract result variable if it exists
            result_obj = execution_result.get("result")
            output = execution_result.get("output", "")
            
            # Process result object
            if result_obj is not None:
                # Convert result to DataFrame if it's not already
                if isinstance(result_obj, pd.DataFrame):
                    if not result_obj.empty:
                        # Reset index to ensure clean display
                        result_df = result_obj.reset_index(drop=True)
                        # Convert to dict, handling NaN values properly
                        try:
                            # Replace NaN with None for JSON serialization
                            result_dict = result_df.where(pd.notna(result_df), None).to_dict('records')
                            results["tables"].append({
                                "name": "analysis_result",
                                "data": result_dict
                            })
                        except Exception as e:
                            print(f"Error converting DataFrame to dict: {e}")
                            # Fallback: convert to string representation
                            results["summary"] = f"DataFrame with {len(result_df)} rows and {len(result_df.columns)} columns:\n{result_df.head(10).to_string()}"
                    else:
                        # Empty DataFrame - add to summary
                        if not results["summary"]:
                            results["summary"] = "Query executed successfully, but returned no results."
                elif isinstance(result_obj, (int, float, np.number)):
                    # Numeric result
                    if not results["summary"]:
                        results["summary"] = f"Result: {result_obj}"
                    else:
                        results["summary"] += f"\n\nResult: {result_obj}"
                elif isinstance(result_obj, (list, tuple)):
                    # List or tuple - try to convert to DataFrame
                    try:
                        df = pd.DataFrame(result_obj)
                        if not df.empty:
                            results["tables"].append({
                                "name": "analysis_result",
                                "data": df.to_dict('records')
                            })
                    except:
                        results["summary"] = str(result_obj) if not results["summary"] else results["summary"] + "\n\n" + str(result_obj)
                else:
                    # Other types - add to summary
                    result_str = str(result_obj)
                    if not results["summary"]:
                        results["summary"] = result_str
                    else:
                        results["summary"] += f"\n\n{result_str}"
            
            # Extract summary from output (append, don't replace)
            if output:
                output_clean = output.strip()
                if output_clean:
                    if results["summary"]:
                        results["summary"] = output_clean + "\n\n" + results["summary"]
                    else:
                        results["summary"] = output_clean
            
            # Check for generated charts (from code execution)
            # Charts might be saved in workspace/charts or current directory
            chart_dirs = [data_manager.charts_dir, Path(".")]
            for chart_dir in chart_dirs:
                if chart_dir.exists():
                    chart_files = list(chart_dir.glob("*.png"))
                    chart_files.extend(list(chart_dir.glob("*.html")))
                    for chart_file in chart_files:
                        results["charts"].append({
                            "type": "image" if chart_file.suffix == ".png" else "html",
                            "title": chart_file.stem,
                            "path": str(chart_file)
                        })
        else:
            results["summary"] = f"Error: {execution_result.get('error', 'Unknown error')}"
        
        # Step 7: Create lineage report
        lineage_report = lineage_tracker.create_lineage_report(
            lineage_info,
            execution_result
        )
        
        # Format lineage for display
        lineage_data = []
        for col in lineage_info.get("columns_used", []):
            lineage_data.append({
                "file": lineage_info.get("file_name", "Unknown"),
                "sheet": lineage_info.get("sheet_name", "Unknown"),
                "column_name": col,
                "normalized_name": col
            })
        
        return {
            "status": "ok" if execution_result["success"] else "error",
            "code": code,
            "results": results,
            "lineage": {
                "columns": lineage_data,
                "explanation": lineage_tracker.format_lineage_for_display(lineage_report)
            },
            "output": execution_result.get("output", "")
        }
    
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        return {
            "status": "error",
            "message": error_msg,
            "code": "",
            "results": {},
            "lineage": {}
        }


def transcribe_audio_stream(audio) -> str:
    """
    Transcribe audio to text (voice input)
    
    Args:
        audio: Audio file path or tuple (file_path, sample_rate) from Gradio Audio component
    
    Returns:
        Transcribed text string
    """
    try:
        if audio is None:
            return ""
        
        # Gradio Audio component returns a tuple: (file_path, sample_rate)
        # or just a file path string
        file_path = None
        if isinstance(audio, tuple):
            file_path = audio[0]
        elif isinstance(audio, str):
            file_path = audio
        
        if not file_path:
            return ""
        
        # Try to use OpenAI Whisper API if available
        try:
            from openai import OpenAI
            from dotenv import load_dotenv
            import os
            
            # Load .env file to ensure API key is available
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            
            if api_key:
                client = OpenAI(api_key=api_key)
                
                # Verify file exists
                if not os.path.exists(file_path):
                    return f"Error: Audio file not found at {file_path}"
                
                # Open the audio file and transcribe
                print(f"Transcribing audio file: {file_path}")
                with open(file_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=None  # Auto-detect language
                    )
                print(f"Transcription successful: {transcript.text[:50]}...")
                return transcript.text
            else:
                # Fallback to mock if no API key
                return "OpenAI API key not found. Please set OPENAI_API_KEY in .env file for voice transcription."
        
        except ImportError:
            return "OpenAI library not installed. Please install: pip install openai"
        
        except Exception as e:
            # If OpenAI API fails, try fallback methods
            print(f"OpenAI transcription failed: {e}")
            
            # Try using speech_recognition library as fallback
            try:
                import speech_recognition as sr
                
                recognizer = sr.Recognizer()
                with sr.AudioFile(file_path) as source:
                    audio_data = recognizer.record(source)
                    # Try Google Speech Recognition (free, no API key needed)
                    try:
                        text = recognizer.recognize_google(audio_data, language="zh-CN,en-US")
                        return text
                    except sr.UnknownValueError:
                        return "Could not understand audio. Please speak more clearly."
                    except sr.RequestError as e:
                        return f"Speech recognition service error: {str(e)}"
            
            except ImportError:
                return "Speech recognition libraries not available. Please install: pip install SpeechRecognition"
            except Exception as e:
                return f"Transcription error: {str(e)}"
    
    except Exception as e:
        print(f"Error in transcription: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}"

