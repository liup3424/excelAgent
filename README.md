# Excel Analysis Agent

An intelligent Excel analysis agent that understands natural language questions, automatically selects relevant Excel files, generates and executes Python analysis code, and provides data lineage tracking.

## Features

- 📊 **Excel Preprocessing**: Handles merged cells, multi-level headers, and complex layouts
- 🧠 **Natural Language Understanding**: Supports Chinese and English queries
- 🐍 **Code Generation**: Automatically generates and executes Python analysis code
- 🔍 **Data Lineage**: Tracks and explains which Excel columns were used
- 🗣️ **Voice Input**: WebSocket-based real-time voice input support

## Project Structure

```
excelAgent/
├── workspace/             # Uploaded Excel files and processed data
│   ├── uploads/          # Excel files uploaded via UI
│   ├── data/             # Preprocessed normalized tables
│   └── charts/           # Generated charts
├── src/
│   ├── preprocessing/      # Excel preprocessing pipeline
│   ├── nlp/               # Natural language understanding
│   ├── codegen/           # Code generation and execution
│   ├── lineage/           # Data lineage tracking
│   ├── websocket/         # WebSocket server
│   └── utils/             # Utility functions
├── data/                  # Preprocessed normalized tables
├── tests/                 # Test cases
└── main.py               # Main entry point
```

## Installation

### Option 1: Using Setup Script (Recommended)

**macOS/Linux:**
```bash
./setup.sh
```

**Windows:**
```bash
setup.bat
```

### Option 2: Manual Setup

1. Create and activate virtual environment:

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Quick Start

### 1. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 2. Start the Gradio UI (Recommended)

```bash
python app_gradio.py
```

Then open your browser to: **http://localhost:7860**

### 3. Use the App

1. **Upload Excel files** via the UI
2. **Ask questions** in Chinese or English (e.g., "列出所有数据" or "Show all data")
3. **View results** in the tabs (Code, Tables, Charts, Summary, Lineage)

## 📖 Complete Usage Guide

See **[HOW_TO_USE.md](HOW_TO_USE.md)** for:
- Step-by-step instructions
- Example questions (Chinese & English)
- Troubleshooting guide
- Advanced usage

## Alternative Modes

### CLI Mode

```bash
python main.py --mode cli
```

### WebSocket Mode

```bash
python main.py --mode websocket
```

## Configuration

Create a `.env` file with your LLM API keys:

```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

