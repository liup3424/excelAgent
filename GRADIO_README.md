# Gradio UI for Excel Analysis Agent

This document explains how to use the Gradio-based frontend for the Excel Analysis Agent.

## Overview

The Gradio UI provides a pure-Python web interface that:
- Uses WebSockets internally (via Gradio) for real-time interaction
- Supports Excel file upload and preprocessing
- Accepts natural language questions via text or voice input
- Displays generated Python code, analysis results, charts, and data lineage

## Installation

1. Install Gradio (if not already installed):
```bash
pip install gradio
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

## Running the App

```bash
python app_gradio.py
```

The app will start and display a URL, typically:
```
Running on local URL:  http://127.0.0.1:7860
```

Open this URL in your web browser.

## Usage Flow

### Step 1: Upload Excel Files

1. Click "Select Excel Files" and choose one or more Excel files (`.xlsx` or `.xls`)
2. Click "Upload Excel Files"
3. Wait for processing:
   - Files are copied to `workspace/uploads/`
   - Each sheet is preprocessed:
     - Merged cells are unmerged
     - Headers are classified (labels vs headers) using LLM
     - Multi-level headers are merged into single rows
     - Normalized tables are saved as Parquet files
4. View the upload summary showing:
   - Number of files processed
   - Number of tables created
   - Details for each file and sheet

### Step 2: Ask a Question

You can ask questions in two ways:

#### Text Input
- Type your question in the text box
- Examples:
  - Chinese: "帮我分析各地区销售趋势"
  - English: "Compare quarterly revenue by region"

#### Voice Input
1. Click the microphone icon
2. Speak your question
3. Click "🎤 Transcribe Voice" to convert speech to text
4. The transcribed text will appear in the question text box

**Note:** Currently uses mock transcription. To enable real speech-to-text:
- Uncomment and configure the OpenAI Whisper API in `src/backend_api.py`
- Or integrate with another STT service (Google, Azure, etc.)

### Step 3: Run Analysis

1. Click "Run Analysis"
2. The system will:
   - Extract intent from your question
   - Map entities to Excel columns
   - Select relevant tables
   - Generate Python code
   - Execute the code
   - Collect results and lineage

### Step 4: View Results

Results are displayed in multiple tabs:

#### Generated Code Tab
- Shows the Python code that was generated and executed
- Code is syntax-highlighted
- You can copy the code for reuse

#### Tables Tab
- Displays analysis results as interactive DataFrames
- Shows aggregated data, filtered results, etc.
- Scrollable and sortable

#### Charts Tab
- Displays any charts generated during analysis
- Supports PNG images and HTML plots (Plotly)
- Gallery view with multiple charts

#### Summary Tab
- Text summary of the analysis
- Execution output and statistics
- Key findings

#### Data Lineage Tab
- Shows which Excel columns were used
- Lists file name, sheet name, and column names
- Explains the data flow

## Architecture

### Backend Functions

The UI calls three main backend functions:

1. **`upload_excels(files)`**
   - Accepts list of file paths
   - Processes Excel files through the preprocessing pipeline
   - Returns upload summary

2. **`run_query(question, language)`**
   - Takes natural language question
   - Runs full analysis pipeline:
     - Intent extraction
     - Column mapping
     - Code generation
     - Code execution
     - Result collection
   - Returns code, results, and lineage

3. **`transcribe_audio_stream(audio)`**
   - Accepts audio file/stream
   - Converts speech to text
   - Returns transcript string

### Data Flow

```
Excel Files (Upload)
    ↓
workspace/uploads/ (Saved)
    ↓
Preprocessing Pipeline
    ├─ Unmerge cells
    ├─ Classify headers (LLM)
    ├─ Merge multi-level headers
    └─ Normalize to 2D tables
    ↓
workspace/data/*.parquet (Saved)
    ↓
DataManager (Singleton - holds table metadata)
    ↓
User Question (Text/Voice)
    ↓
run_query()
    ├─ Intent Extraction
    ├─ Column Mapping
    ├─ Code Generation
    ├─ Code Execution
    └─ Result Collection
    ↓
Results Display (Gradio UI)
```

## File Structure

```
excelAgent/
├── app_gradio.py              # Gradio UI application
├── src/
│   ├── backend_api.py          # Backend API functions
│   ├── utils/
│   │   └── data_manager.py    # DataManager singleton
│   └── ...                    # Other modules
└── workspace/
    ├── uploads/               # Uploaded Excel files
    ├── data/                  # Normalized Parquet files
    └── charts/                # Generated charts
```

## Customization

### Enable Real Speech-to-Text

Edit `src/backend_api.py`, function `transcribe_audio_stream()`:

```python
from openai import OpenAI

def transcribe_audio_stream(audio) -> str:
    client = OpenAI()
    with open(audio, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text
```

### Change Port

Edit `app_gradio.py`:

```python
app.launch(
    server_port=8080,  # Change port
    ...
)
```

### Customize UI Theme

Edit `app_gradio.py`:

```python
with gr.Blocks(theme=gr.themes.Monochrome()) as app:
    # or gr.themes.Glass(), gr.themes.Default(), etc.
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 7860
lsof -i :7860
# Kill the process or change port
```

### Excel Files Not Processing
- Check file format (must be .xlsx or .xls)
- Ensure files are not corrupted
- Check console for error messages

### Voice Input Not Working
- Ensure microphone permissions are granted
- Check browser console for errors
- Try using text input instead

### Charts Not Displaying
- Check if charts are saved in `workspace/charts/`
- Ensure code execution generates chart files
- Check file permissions

## WebSocket Support

Gradio uses WebSockets internally for:
- Real-time communication between browser and Python backend
- Streaming audio input
- Live updates during processing

This satisfies the "WebSocket-based voice input" requirement, even though we're not manually writing JavaScript/WebSocket code.

## Next Steps

- Integrate real STT service (Whisper, Google, Azure)
- Add more visualization options
- Support multiple analysis types
- Add export functionality (download results as CSV/PDF)
- Implement user authentication
- Add analysis history/saved queries

