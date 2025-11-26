# Architecture Documentation

## Overview

The Excel Analysis Agent is a comprehensive system that processes natural language questions, automatically selects relevant Excel files, generates Python analysis code, executes it safely, and provides data lineage tracking.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input Layer                          │
│  ┌──────────────┐              ┌──────────────┐            │
│  │  CLI Mode    │              │  WebSocket   │            │
│  │  (Text)      │              │  (Voice/Text)│            │
│  └──────┬───────┘              └──────┬───────┘            │
└─────────┼─────────────────────────────┼────────────────────┘
          │                             │
          └─────────────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │    Excel Analysis Agent        │
        │    (Main Orchestrator)         │
        └───────────────┬───────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ Preprocessing│ │     NLP     │ │  Code Gen   │
│   Pipeline   │ │  Pipeline   │ │  & Execute  │
└───────┬──────┘ └──────┬──────┘ └──────┬──────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │      Lineage Tracking         │
        └───────────────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │         Results Output         │
        │  (Code + Results + Lineage)   │
        └───────────────────────────────┘
```

## Component Details

### 1. Preprocessing Pipeline (`src/preprocessing/`)

#### 1.1 UnmergeProcessor (`unmerge.py`)
- **Purpose**: Handle merged cells in Excel files
- **Process**:
  1. Load Excel file using `openpyxl`
  2. Store merged cell information
  3. Unmerge all merged cells
  4. Fill blank cells in previously merged regions with the original value
- **Output**: DataFrame with no merged cells, all values filled

#### 1.2 HeaderAnalyzer (`header_analysis.py`)
- **Purpose**: Classify rows as labels vs headers using LLM
- **Process**:
  1. Extract top N rows (sample) from sheet
  2. Format sample for LLM input
  3. Call LLM to classify rows:
     - `labels`: Descriptive text to remove
     - `header`: Table header rows to keep
  4. Return JSON with row classifications
- **Output**: Dictionary with `labels` and `header` row indices

#### 1.3 TableNormalizer (`normalization.py`)
- **Purpose**: Clean and normalize sheets to 2D tables
- **Process**:
  1. Remove rows classified as `labels`
  2. Merge multi-level headers into single header row
  3. Clean DataFrame (remove empty rows/columns)
  4. Infer column types (numeric, datetime, categorical)
- **Output**: Normalized DataFrame + metadata

### 2. NLP Pipeline (`src/nlp/`)

#### 2.1 IntentExtractor (`intent_extraction.py`)
- **Purpose**: Extract analysis intent from natural language
- **Extracts**:
  - Intent type: aggregation, grouping, trend, filter, sort, comparison
  - Operations: sum, average, count, min, max
  - Group by columns
  - Filter conditions
  - Sort configuration
  - Entities (region, sales, date, etc.)
  - Selected tables
- **Output**: Structured intent dictionary

#### 2.2 ColumnMapper (`column_mapping.py`)
- **Purpose**: Map entities to actual Excel columns
- **Process**:
  1. Map extracted entities to columns using similarity matching
  2. Infer columns from intent (e.g., numeric columns for metrics)
  3. Handle date columns for trend analysis
- **Output**: Dictionary mapping entity types to column names

### 3. Code Generation & Execution (`src/codegen/`)

#### 3.1 CodeGenerator (`generator.py`)
- **Purpose**: Generate Python code for analysis
- **Generates**:
  - Import statements (pandas, numpy, matplotlib, plotly)
  - Data loading code
  - Filter code
  - Group by and aggregation code
  - Sort code
  - Visualization code (when needed)
  - Display code
- **Output**: Complete Python code string + lineage metadata

#### 3.2 CodeExecutor (`executor.py`)
- **Purpose**: Safely execute generated code
- **Features**:
  - Captures stdout/stderr
  - Handles errors gracefully
  - Provides helpful error suggestions
  - Returns execution results
- **Output**: Execution result dictionary (success, output, error, result)

### 4. Data Lineage (`src/lineage/`)

#### 4.1 LineageTracker (`tracker.py`)
- **Purpose**: Track and report which columns were used
- **Tracks**:
  - File name and sheet name
  - Columns used in analysis
  - Operations performed
  - Success status
- **Output**: Human-readable lineage report

### 5. WebSocket Server (`src/websocket/`)

#### 5.1 WebSocketServer (`server.py`)
- **Purpose**: Handle real-time voice/text input via WebSocket
- **Features**:
  - FastAPI-based WebSocket server
  - Accepts audio (base64 encoded) or text
  - Mock STT (can be replaced with real STT service)
  - Processes queries through analysis agent
  - Returns results via WebSocket
- **Endpoints**:
  - `GET /`: HTML page
  - `WS /ws`: WebSocket endpoint

### 6. Main Agent (`src/agent.py`)

#### 6.1 ExcelAnalysisAgent
- **Purpose**: Main orchestrator that coordinates all components
- **Responsibilities**:
  1. Initialize all components
  2. Preprocess all Excel files on startup
  3. Cache normalized tables
  4. Process user questions through full pipeline
  5. Return comprehensive results
- **Methods**:
  - `_preprocess_all_files()`: Preprocess all Excel files
  - `analyze(question)`: Main analysis method

## Data Flow

### Preprocessing Flow
```
Excel File → UnmergeProcessor → HeaderAnalyzer → TableNormalizer → Normalized Table (Parquet)
```

### Analysis Flow
```
User Question → IntentExtractor → ColumnMapper → CodeGenerator → CodeExecutor → LineageTracker → Results
```

## File Structure

```
excelAgent/
├── excelExample/          # Input Excel files
├── data/                  # Preprocessed normalized tables (Parquet)
├── src/
│   ├── preprocessing/     # Excel preprocessing pipeline
│   ├── nlp/              # Natural language understanding
│   ├── codegen/          # Code generation and execution
│   ├── lineage/          # Data lineage tracking
│   ├── websocket/        # WebSocket server
│   ├── utils/            # Utility functions
│   └── agent.py          # Main agent
├── tests/                # Test cases and examples
├── main.py              # Entry point
├── requirements.txt     # Dependencies
└── README.md           # Documentation
```

## Key Design Decisions

1. **Modular Architecture**: Each component is independent and can be extended/replaced
2. **LLM Integration**: Uses OpenAI API for header classification and intent extraction (with fallback to rule-based)
3. **Safe Code Execution**: Executes code in controlled environment with error handling
4. **Data Lineage**: Tracks all columns used for transparency
5. **Caching**: Preprocessed tables are cached as Parquet files for performance
6. **Extensibility**: Easy to add new analysis types, visualization options, or STT services

## Extension Points

1. **STT Service**: Replace mock STT in `WebSocketServer._process_audio()` with real service
2. **LLM Provider**: Can switch from OpenAI to Anthropic or other providers
3. **Visualization**: Add more chart types in `CodeGenerator._generate_visualization_code()`
4. **Analysis Types**: Add new intent types in `IntentExtractor`
5. **Header Patterns**: Improve header merging strategies in `TableNormalizer`

## Error Handling

- **Preprocessing Errors**: Logged, file skipped, continue with others
- **LLM Errors**: Fallback to rule-based extraction
- **Code Execution Errors**: Captured, suggestions provided
- **Column Mapping Errors**: Uses similarity matching with threshold

## Performance Considerations

- Preprocessing happens once on startup
- Normalized tables cached as Parquet (fast loading)
- LLM calls can be cached for similar questions
- Code execution is synchronous (can be made async for WebSocket)

