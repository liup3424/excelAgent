# How to Use Excel Analysis Agent

## 🚀 Quick Start

### 1. Setup (One-time)

```bash
# Navigate to project directory
cd /Users/fionaliu/PycharmProjects/excelAgent

# Activate virtual environment
source venv/bin/activate

# (If not already installed) Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys (Optional but Recommended)

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Note:** Without the API key, the system will use fallback rule-based methods which are less accurate.

### 3. Start the Gradio UI

```bash
python app_gradio.py
```

You should see:
```
Running on local URL:  http://127.0.0.1:7860
```

Open your browser to: **http://localhost:7860**

---

## 📖 Step-by-Step Usage Guide

### Step 1: Upload Excel Files

1. **In the browser**, you'll see the Excel Analysis Agent interface
2. **In the "Step 1: Upload Excel Files" section:**
   - Click "Select Excel Files" or drag and drop files
   - Select one or more Excel files (`.xlsx` or `.xls` format)
   - Click "Upload Excel Files" button
3. **Wait for processing** (10-30 seconds per file):
   - The system automatically:
     - Unmerges merged cells
     - Classifies headers using LLM
     - Merges multi-level headers
     - Normalizes tables
   - Files are saved to `workspace/uploads/`
   - Processed tables are saved to `workspace/data/`
4. **Check the upload status:**
   - You should see: "✓ Successfully uploaded X file(s) with Y table(s)!"
   - The upload summary shows file and sheet details

### Step 2: Ask a Question

You can ask questions in **two ways**:

#### Option A: Text Input
1. Type your question in the text box
2. Examples:
   - **Chinese**: "列出所有数据", "分析各地区销售趋势", "计算总销售额"
   - **English**: "Show all data", "Analyze sales trends by region", "Calculate total sales"
3. Click "Run Analysis"

#### Option B: Voice Input
1. Click the microphone icon
2. Speak your question
3. Click "🎤 Transcribe Voice" to convert speech to text
4. The transcribed text appears in the question box
5. Click "Run Analysis"

**Note:** Voice transcription currently uses a mock implementation. To enable real STT, edit `src/backend_api.py` and configure OpenAI Whisper or another STT service.

### Step 3: View Results

After clicking "Run Analysis", wait a few seconds, then check the **5 tabs**:

#### Tab 1: Generated Code
- View the Python code that was generated
- Code is syntax-highlighted
- You can copy the code for reuse

#### Tab 2: Tables
- View analysis results as interactive DataFrames
- Scrollable and sortable tables
- Shows aggregated data, filtered results, etc.

#### Tab 3: Charts
- View any charts generated during analysis
- Supports PNG images and HTML plots (Plotly)
- Gallery view with multiple charts

#### Tab 4: Summary
- Text summary of the analysis
- Execution output and statistics
- Key findings and insights

#### Tab 5: Data Lineage
- Shows which Excel columns were used
- Lists file name, sheet name, and column names
- Explains the data flow

---

## 💡 Example Questions

### Chinese Questions
- "列出所有数据" - List all data
- "分析各地区销售趋势" - Analyze sales trends by region
- "计算每个产品的总销售额" - Calculate total sales per product
- "找出销售额最高的前10个产品" - Find top 10 products by sales
- "比较不同地区的平均销售额" - Compare average sales across regions
- "显示前20行数据" - Show first 20 rows

### English Questions
- "Show all data"
- "Analyze sales trends by region"
- "Calculate total sales for each product"
- "Find the top 10 products by sales"
- "Compare average sales across regions"
- "Display first 20 rows"

### Complex Questions
- "帮我找出2023年销售额超过100万的地区，并按销售额从高到低排序"
- "分析每个产品类别在过去6个月的平均销售额趋势"
- "比较Q1和Q2的销售数据，找出增长最快的产品"

---

## 🎯 Use Cases

### 1. Data Exploration
**Question**: "列出所有数据" or "Show all data"
**Result**: Displays the entire table

### 2. Aggregation Analysis
**Question**: "计算总销售额" or "Calculate total sales"
**Result**: Shows aggregated statistics

### 3. Grouping Analysis
**Question**: "按地区分组统计销售额" or "Group sales by region"
**Result**: Shows grouped and aggregated data

### 4. Trend Analysis
**Question**: "分析月度销售趋势" or "Analyze monthly sales trends"
**Result**: Shows time series data and charts

### 5. Top N Analysis
**Question**: "找出销售额最高的前10个产品" or "Find top 10 products by sales"
**Result**: Shows sorted and filtered results

---

## 🔧 Advanced Usage

### CLI Mode (Alternative to UI)

If you prefer command line:

```bash
# Start CLI mode
python main.py --mode cli

# Or with a directory of Excel files
python main.py --mode cli --excel-dir /path/to/excel/files
```

Then type questions interactively.

### WebSocket Mode

For programmatic access:

```bash
python main.py --mode websocket --port 8000
```

Connect to `ws://localhost:8000/ws` and send:
- Text: `{"type": "text", "text": "your question"}`
- Audio: `{"type": "audio", "data": "base64_encoded_audio"}`

---

## 📁 File Structure

```
excelAgent/
├── workspace/              # Created automatically
│   ├── uploads/          # Excel files uploaded via UI
│   ├── data/             # Preprocessed normalized tables (Parquet)
│   └── charts/           # Generated charts
├── src/                   # Source code
├── app_gradio.py         # Gradio UI (main entry point)
├── main.py               # CLI/WebSocket entry point
└── requirements.txt      # Dependencies
```

---

## ⚠️ Troubleshooting

### App Won't Start
- **Check port**: Make sure port 7860 is not in use
- **Check dependencies**: Run `pip install -r requirements.txt`
- **Check Python version**: Requires Python 3.9+

### Upload Fails
- **File format**: Ensure files are `.xlsx` or `.xls`
- **File size**: Very large files may take longer
- **Check terminal**: Look for error messages

### Analysis Fails
- **Upload first**: Make sure files are uploaded before asking questions
- **Check API key**: Ensure OpenAI API key is set in `.env` for better accuracy
- **Check question**: Make sure the question is clear and understandable
- **View code tab**: Check the generated code for issues

### No Results Showing
- **Wait longer**: Processing takes time (especially with LLM calls)
- **Check Summary tab**: May contain error messages
- **Check terminal**: Look for detailed error logs

### Voice Input Not Working
- **Microphone permissions**: Grant browser microphone access
- **Browser compatibility**: Use Chrome, Firefox, or Edge
- **Use text input**: As an alternative

---

## 🎓 Tips for Best Results

1. **Clear Questions**: Be specific about what you want
   - ✅ Good: "计算每个地区的总销售额"
   - ❌ Vague: "分析数据"

2. **Upload Quality Files**: 
   - Files with clear headers work best
   - Complex merged cells may take longer to process

3. **Use API Key**: 
   - Better header classification
   - More accurate intent extraction
   - Better column mapping

4. **Check Data Lineage**: 
   - Always verify which columns were used
   - Ensures the analysis is correct

5. **Review Generated Code**: 
   - Understand what analysis was performed
   - Modify and reuse code if needed

---

## 🔄 Workflow Example

1. **Start app**: `python app_gradio.py`
2. **Open browser**: http://localhost:7860
3. **Upload file**: Select Excel file → Click "Upload Excel Files"
4. **Wait**: Processing takes 10-30 seconds
5. **Ask question**: Type "列出所有数据" → Click "Run Analysis"
6. **View results**: Check all 5 tabs
7. **Ask more questions**: Try different analyses
8. **Upload more files**: Add additional Excel files as needed

---

## 📚 Additional Resources

- **Architecture**: See `ARCHITECTURE.md` for technical details
- **Implementation**: See `IMPLEMENTATION_SUMMARY.md` for design decisions
- **Gradio Guide**: See `GRADIO_README.md` for UI-specific details
- **Examples**: See `tests/test_examples.py` for example questions

---

## 🆘 Getting Help

If you encounter issues:

1. **Check terminal output** for error messages
2. **Check browser console** (F12) for frontend errors
3. **Review logs** in the terminal
4. **Verify API key** is set correctly
5. **Check file format** (must be .xlsx or .xls)

---

## ✨ Features Summary

- ✅ **Upload multiple Excel files** via drag-and-drop
- ✅ **Automatic preprocessing** (unmerge, header classification, normalization)
- ✅ **Natural language questions** (Chinese and English)
- ✅ **Voice input** (microphone support)
- ✅ **Automatic code generation** (Python/pandas)
- ✅ **Interactive results** (tables, charts, summaries)
- ✅ **Data lineage tracking** (see which columns were used)
- ✅ **WebSocket support** (real-time communication)

Enjoy using the Excel Analysis Agent! 🎉

