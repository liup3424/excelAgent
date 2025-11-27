# Quick Test Guide for Gradio UI

## 🚀 Step-by-Step Testing Instructions

### 1. Start the App

The app should be starting. Wait a few seconds, then:

**Open your web browser and go to:**
```
http://localhost:7860
```

Or if that doesn't work, try:
```
http://127.0.0.1:7860
```

### 2. Upload an Excel File

1. **In the browser**, you'll see the Excel Analysis Agent interface
2. **In the "Step 1: Upload Excel Files" section:**
   - Click "Select Excel Files" or the file upload area
   - Navigate to any folder containing Excel files
   - Choose an Excel file (`.xlsx` or `.xls` format)
   - Click "Open" to select the file
3. **Click "Upload Excel Files" button**
4. **Wait for processing** (this may take 10-30 seconds):
   - The system will preprocess the Excel file
   - Unmerge cells
   - Classify headers using LLM
   - Normalize the table
5. **Check the upload status:**
   - You should see: "✓ Successfully uploaded 1 file(s) with X table(s)!"
   - The upload summary will show file and sheet details

### 3. Ask a Question

**Option A: Text Input**
1. In the "Step 2: Ask a Question" section
2. Type a question in the text box, for example:
   - **Chinese**: "列出所有数据" or "分析数据"
   - **English**: "Show all data" or "Analyze the data"
3. Click "Run Analysis"

**Option B: Voice Input (Optional)**
1. Click the microphone icon
2. Speak your question
3. Click "🎤 Transcribe Voice"
4. The transcribed text will appear in the question box
5. Click "Run Analysis"

### 4. View Results

After clicking "Run Analysis", wait a few seconds, then check the tabs:

1. **Generated Code Tab:**
   - See the Python code that was generated
   - Code is syntax-highlighted

2. **Tables Tab:**
   - View the analysis results as a table
   - Scrollable and interactive

3. **Charts Tab:**
   - See any charts generated (if applicable)

4. **Summary Tab:**
   - Read the analysis summary
   - See execution output

5. **Data Lineage Tab:**
   - See which Excel columns were used
   - View file and sheet information

## 🧪 Test Scenarios

### Test 1: Simple Data Display
**Question**: "列出所有数据" or "Show all data"
**Expected**: Should display the entire table

### Test 2: Data Analysis
**Question**: "分析数据" or "Analyze the data"
**Expected**: Should generate analysis code and show results

### Test 3: Complex Headers
**File**: `复杂表头.xlsx`
**Question**: "分析这个表格" or "Analyze this table"
**Expected**: Should handle multi-level headers correctly

## ⚠️ Troubleshooting

### App Not Loading?
- Check terminal for errors
- Make sure port 7860 is not in use
- Try restarting: Stop the app (Ctrl+C) and run `python app_gradio.py` again

### Upload Fails?
- Check that the Excel file is not corrupted
- Ensure file is .xlsx or .xls format
- Check terminal for error messages

### Analysis Fails?
- Make sure files are uploaded first
- Check that your OpenAI API key is set in `.env`
- Look at the "Generated Code" tab to see what code was generated
- Check terminal for detailed error messages

### No Results Showing?
- Wait a bit longer (processing takes time)
- Check the "Summary" tab for error messages
- Verify the question is clear and understandable

## 📝 Example Questions to Try

**Chinese:**
- "列出所有数据"
- "分析数据"
- "显示前10行"
- "计算总和"

**English:**
- "Show all data"
- "Analyze the data"
- "Display first 10 rows"
- "Calculate total"

## 🎯 What to Look For

✅ **Successful Upload:**
- Green checkmark or success message
- Upload summary shows file and sheet info
- No error messages

✅ **Successful Analysis:**
- Generated code appears in Code tab
- Results appear in Tables tab
- Summary shows analysis output
- Data lineage shows which columns were used

Enjoy testing! 🚀

