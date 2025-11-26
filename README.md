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
├── excelExample/          # Input Excel files
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

## Usage

Make sure the virtual environment is activated, then:

```bash
# CLI mode
python main.py --mode cli

# WebSocket mode
python main.py --mode websocket
```

## Configuration

Create a `.env` file with your LLM API keys:

```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

