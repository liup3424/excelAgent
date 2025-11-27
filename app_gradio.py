"""
Gradio UI for Excel Analysis Agent

This is a pure-Python frontend using Gradio that provides:
- Excel file upload and preprocessing
- Natural language question input (text and voice)
- Display of generated code, results, charts, and data lineage

Run with: python app_gradio.py
"""

import gradio as gr
from pathlib import Path
import json
# Removed type hints to avoid Gradio JSON schema parsing issues

from src.backend_api import upload_excels, run_query, transcribe_audio_stream
from src.utils.data_manager import DataManager


def handle_file_upload(files):
    """
    Handle Excel file upload
    
    Args:
        files: List of file paths from Gradio File component
    
    Returns:
        Tuple of (status message, JSON summary)
    """
    if not files:
        return "Please select Excel files to upload.", "{}"
    
    try:
        result = upload_excels(files)
        
        if result["status"] == "ok":
            summary = {
                "status": "success",
                "files_processed": result["num_files"],
                "total_tables": result["total_tables"],
                "files": result["tables"]
            }
            message = f"✓ Successfully uploaded {result['num_files']} file(s) with {result['total_tables']} table(s)!"
        else:
            summary = result
            message = f"✗ Error: {result.get('message', 'Unknown error')}"
        
        summary_text = json.dumps(summary, indent=2, ensure_ascii=False)
        return message, summary_text
    
    except Exception as e:
        error_msg = f"Error uploading files: {str(e)}"
        return error_msg, json.dumps({"status": "error", "message": error_msg}, indent=2)


def handle_voice_input(audio):
    """
    Handle voice input and transcribe to text
    
    Args:
        audio: Audio input from Gradio Audio component (tuple of (file_path, sample_rate) or file path string)
    
    Returns:
        Transcribed text
    """
    if audio is None:
        return ""
    
    try:
        # Debug: print what we received
        print(f"[DEBUG] Audio input type: {type(audio)}, value: {audio}")
        
        # Extract file path from Gradio audio format
        file_path = None
        if isinstance(audio, tuple) and len(audio) > 0:
            file_path = audio[0]
        elif isinstance(audio, str):
            file_path = audio
        
        if not file_path:
            print("[DEBUG] No file path extracted from audio input")
            return "No audio file found. Please record again."
        
        print(f"[DEBUG] Using file path: {file_path}")
        
        transcript = transcribe_audio_stream(audio)
        
        print(f"[DEBUG] Transcription result: {transcript[:100] if transcript else 'None'}...")
        
        if not transcript or transcript.strip() == "":
            return "No transcription available. Please try recording again or check your OpenAI API key."
        
        return transcript
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Error in handle_voice_input: {error_details}")
        return f"Error transcribing audio: {str(e)}"


def handle_analysis(question):
    """
    Handle analysis query
    
    Args:
        question: Natural language question
    
    Returns:
        Tuple of (code, results_dict, summary, lineage)
    """
    if not question or not question.strip():
        return "", {}, "Please enter a question.", ""
    
    try:
        result = run_query(question, language="auto")
        
        if result["status"] == "error":
            error_msg = result.get("message", "Unknown error")
            return "", {}, f"✗ Error: {error_msg}", ""
        
        # Extract results
        code = result.get("code", "")
        results = result.get("results", {})
        
        # Get summary from results (which includes execution output)
        summary = results.get("summary", "")
        if not summary:
            # Fallback to output if summary is empty
            summary = result.get("output", "")
        
        lineage = result.get("lineage", {})
        
        # Format lineage
        lineage_text = lineage.get("explanation", "")
        if lineage.get("columns"):
            lineage_text += "\n\nColumns used:\n"
            for col_info in lineage["columns"]:
                lineage_text += f"- {col_info.get('column_name', 'Unknown')} (from {col_info.get('file', 'Unknown')}/{col_info.get('sheet', 'Unknown')})\n"
        
        return code, results, summary, lineage_text
    
    except Exception as e:
        error_msg = f"Error running analysis: {str(e)}"
        return "", {}, f"✗ {error_msg}", ""


def format_results_for_display(results):
    """
    Format results for Gradio components
    
    Args:
        results: Results dictionary from run_query
    
    Returns:
        Tuple of (dataframe, chart_html, chart_images, summary_text)
    """
    import pandas as pd
    
    if not results or not isinstance(results, dict):
        return pd.DataFrame(), "", [], ""  # Return empty DataFrame instead of None
    
    # Extract tables - use the result table from code execution
    tables = results.get("tables", [])
    df = pd.DataFrame()  # Default to empty DataFrame
    if tables:
        # Use the table named "analysis_result" (from code execution) if available
        # Otherwise use the first table
        result_table = None
        for table in tables:
            if table.get("name") == "analysis_result":
                result_table = table
                break
        
        if result_table is None and tables:
            result_table = tables[0]
        
        if result_table:
            data = result_table.get("data", [])
            if data:
                try:
                    df = pd.DataFrame(data)
                    # Ensure we have a proper DataFrame
                    if df.empty:
                        df = pd.DataFrame()
                except Exception as e:
                    print(f"Error creating DataFrame from table data: {e}")
                    df = pd.DataFrame()  # Return empty DataFrame on error
    
    # Extract charts - separate HTML and images
    # Only process if charts exist in results
    charts = results.get("charts", [])
    chart_images = []
    html_charts = []
    
    if charts:
        for chart in charts:
            chart_path = chart.get("path", "")
            chart_type = chart.get("type", "")
            
            if chart_path and Path(chart_path).exists():
                if chart_type == "html" or chart_path.endswith(".html"):
                    # Read HTML content
                    try:
                        with open(chart_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        html_charts.append(html_content)
                    except Exception as e:
                        print(f"Error reading HTML chart {chart_path}: {e}")
                elif chart_path.endswith((".png", ".jpg", ".jpeg")):
                    chart_images.append(chart_path)
    
    # Combine HTML charts into a single HTML string
    # Embed Plotly HTML directly - Gradio HTML component supports full HTML
    if html_charts:
        html_display = "<div style='display: flex; flex-direction: column; gap: 20px; width: 100%;'>"
        for i, html_content in enumerate(html_charts):
            html_display += f"<div style='border: 1px solid #ddd; border-radius: 8px; padding: 10px; margin-bottom: 20px; width: 100%; background: white;'>"
            html_display += f"<h4 style='margin-top: 0; margin-bottom: 10px; color: #333;'>Chart {i+1}</h4>"
            # Embed HTML directly - Gradio HTML component can handle full Plotly HTML
            html_display += f"<div style='width: 100%; min-height: 400px;'>"
            html_display += html_content
            html_display += "</div>"
            html_display += "</div>"
        html_display += "</div>"
    else:
        html_display = "<p style='padding: 20px; text-align: center; color: #666;'>No interactive charts generated. Charts will appear here when visualization is requested.</p>"
    
    # Extract summary
    summary = results.get("summary", "")
    
    return df, html_display, chart_images, summary


# Create Gradio interface
with gr.Blocks(title="Excel Analysis Agent", theme=gr.themes.Soft()) as app:
    gr.Markdown("""
    # 📊 Excel Analysis Agent
    
    An intelligent Excel analysis tool that understands natural language questions, 
    automatically processes Excel files, and generates Python analysis code.
    
    **Features:**
    - 📁 Upload multiple Excel files with complex headers
    - 🧠 Natural language questions (Chinese or English)
    - 🗣️ Voice input support
    - 🐍 Automatic Python code generation
    - 📈 Interactive results with tables and charts
    - 🔍 Data lineage tracking
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📁 Step 1: Upload Excel Files")
            
            file_upload = gr.File(
                label="Select Excel Files",
                file_count="multiple",
                file_types=[".xlsx", ".xls"],
                height=100
            )
            
            upload_btn = gr.Button("Upload Excel Files", variant="primary")
            
            upload_status = gr.Textbox(
                label="Upload Status",
                interactive=False,
                lines=2
            )
            
            upload_summary = gr.Textbox(
                label="Upload Summary",
                visible=True,
                lines=5,
                interactive=False
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 💬 Step 2: Ask a Question")
            
            question_input = gr.Textbox(
                label="Question (Chinese or English)",
                placeholder="Example: 帮我分析各地区销售趋势\nExample: Compare quarterly revenue by region",
                lines=3
            )
            
            with gr.Row():
                voice_input = gr.Audio(
                    label="Voice Input (Microphone)",
                    sources=["microphone"],
                    type="filepath"
                )
                
                transcribe_btn = gr.Button("🎤 Transcribe Voice", size="sm")
            
            analyze_btn = gr.Button("Run Analysis", variant="primary", size="lg")
    
    with gr.Row():
        gr.Markdown("### 📊 Step 3: View Results")
    
    with gr.Tabs():
        with gr.Tab("Generated Code"):
            code_display = gr.Code(
                label="Generated Python Code",
                language="python",
                lines=20,
                interactive=False
            )
        
        with gr.Tab("Tables"):
            results_dataframe = gr.Dataframe(
                label="Analysis Results",
                interactive=False,
                wrap=True
            )
        
        with gr.Tab("Charts"):
            # Use HTML component for interactive charts (HTML files)
            charts_html = gr.HTML(
                label="Generated Charts (Interactive)",
                value="<p>No charts generated yet. Run an analysis that includes visualization.</p>"
            )
            
            # Gallery for static images (PNG/JPG)
            charts_gallery = gr.Gallery(
                label="Chart Images",
                show_label=True,
                elem_id="gallery",
                columns=2,
                rows=1,
                height="auto",
                value=[]  # Initialize with empty list
            )
        
        with gr.Tab("Summary"):
            summary_display = gr.Markdown(
                label="Analysis Summary",
                value=""
            )
        
        with gr.Tab("Data Lineage"):
            lineage_display = gr.Markdown(
                label="Data Lineage",
                value=""
            )
    
    # Define process function outside to avoid closure issues
    def process_analysis_results(question):
        """Process analysis and format all outputs"""
        import pandas as pd
        
        if not question or not question.strip():
            empty_df = pd.DataFrame()
            return "", empty_df, "", [], "Please enter a question.", ""
        
        code, results, summary, lineage = handle_analysis(question)
        
        # Format results for display
        if results and isinstance(results, dict):
            df, html_charts, chart_images, summary_text = format_results_for_display(results)
        else:
            df = pd.DataFrame()
            html_charts = "<p>No charts generated.</p>"
            chart_images = []
            summary_text = ""
        
        # Ensure df is not None
        if df is None:
            df = pd.DataFrame()
        
        # Return list of image charts for Gallery component
        # Gallery expects a list of image paths
        chart_list = chart_images if chart_images else []
        
        # Combine summary - prefer the summary from handle_analysis
        if summary:
            full_summary = summary
        elif summary_text:
            full_summary = summary_text
        else:
            full_summary = "Analysis completed. Check the Tables tab for results."
        
        return code, df, html_charts, chart_list, full_summary, lineage
    
    # Event handlers
    upload_btn.click(
        fn=handle_file_upload,
        inputs=[file_upload],
        outputs=[upload_status, upload_summary]
    )
    
    transcribe_btn.click(
        fn=handle_voice_input,
        inputs=[voice_input],
        outputs=[question_input]
    )
    
    # Connect analyze button
    analyze_btn.click(
        fn=process_analysis_results,
        inputs=[question_input],
        outputs=[code_display, results_dataframe, charts_html, charts_gallery, summary_display, lineage_display]
    )


if __name__ == "__main__":
    # Initialize data manager
    data_manager = DataManager()
    data_manager.initialize_directories()
    
    # Launch app
    # Disable API to avoid JSON schema parsing bug in Gradio
    import os
    os.environ["GRADIO_SERVER_NAME"] = "127.0.0.1"
    
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        inbrowser=False,
        show_api=False  # Disable API to avoid the bug
    )

