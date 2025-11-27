# LLM-Based Code Generation

## Overview

The code generator now uses **LLM (Large Language Model)** to generate Python analysis code, providing more intelligent and context-aware code generation compared to rule-based approaches.

## How It Works

### 1. LLM-Only Generation

The `CodeGenerator` class uses **only LLM-based code generation**:

- **LLM Mode**: Uses OpenAI GPT to generate code based on comprehensive prompts
- **Required**: `OPENAI_API_KEY` must be set in `.env` file
- **Error Handling**: Raises clear error if API key is missing or LLM call fails

## LLM Prompt Structure

The LLM receives a comprehensive prompt that includes:

### Context Information
- File path and sheet name
- Column names and types
- Row count
- User's question
- Analysis intent (operations, group by, filters, sort)
- Column mappings (entities → actual columns)

### Processing Rules
1. **Basic Code Structure**
   - Required imports (pandas, numpy, plotly)
   - Display settings
   - Output format requirements

2. **Data Query and Processing**
   - Multi-row data handling
   - Time field conversion (`pd.to_datetime`)
   - Numeric field conversion (`pd.to_numeric`)
   - Identifier field handling (`.astype(str)`)

3. **Code Robustness**
   - Exception handling (try-except)
   - Data validation (check `df.empty`, verify columns)
   - Error messages

4. **Naming Conventions**
   - English variable names
   - No special characters
   - Meaningful names

5. **Visualization Requirements**
   - Plotly interactive charts
   - Save to `workspace/charts/analysis_result.html`
   - Proper layout (title, axis labels)

## Benefits of LLM-Based Generation

### Advantages
- ✅ **More Intelligent**: Understands context and intent better
- ✅ **Flexible**: Handles complex queries that rule-based can't
- ✅ **Better Error Handling**: Generates robust code with proper exception handling
- ✅ **Type Safety**: Properly handles data type conversions
- ✅ **Adaptive**: Can handle edge cases and unusual data structures

### Requirements
- ⚠️ **LLM Required**: `OPENAI_API_KEY` must be set in `.env` file
- ⚠️ **No Fallback**: System will raise error if LLM is unavailable
- ✅ **Clear Errors**: Provides helpful error messages if API key is missing

## Configuration

### Enable LLM Mode

1. **Set API Key** in `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

2. **Restart the application**

3. **Verify**:
```python
from src.codegen.generator import CodeGenerator
cg = CodeGenerator()
print(cg.use_llm)  # Should be True if API key is set
```

### Customize LLM Model

Edit `src/codegen/generator.py`, method `_call_llm_for_code()`:

```python
model="gpt-4o-mini"  # Fast and cost-effective
# or
model="gpt-4"  # Better quality, more expensive
```

## Code Generation Flow

```
User Question
    ↓
Intent Extraction
    ↓
Column Mapping
    ↓
CodeGenerator.generate_code()
    ↓
┌─────────────────┐
│   LLM Mode      │
│   (required)    │
└─────────────────┘
    ↓
Generated Python Code
    ↓
Code Execution
    ↓
Results + Lineage
```

## Example Prompt (English)

The LLM receives a prompt like this:

```
You are an expert Python data analyst specializing in Excel data processing with pandas.

**Task**: Generate Python code to answer the user's question about Excel data.

**Excel File Information**:
- File Path: workspace/data/file_sheet.parquet
- Sheet Name: Sheet1
- Total Rows: 100
- Columns (5):
  - sales (numeric)
  - region (categorical)
  - date (datetime)
  ...

**User Question**: Calculate total sales by region

**Analysis Intent**:
Intent Type: grouping
Operations: sum
Group By: region
...

**Excel Data Processing Rules**
[Comprehensive rules about code structure, data handling, error handling, etc.]

**Generate the Python code now**:
```

## Generated Code Quality

The LLM generates code that:

- ✅ Includes proper imports and settings
- ✅ Has try-except error handling
- ✅ Validates data before processing
- ✅ Handles data types correctly
- ✅ Prints results to console
- ✅ Saves visualizations properly
- ✅ Follows pandas best practices

## Monitoring

To see which mode is being used:

```python
# In your code
code, lineage = code_generator.generate_code(...)
# Check terminal output for "LLM code generation" or "falling back to rule-based"
```

## Troubleshooting

### LLM Not Being Used

1. **Check API Key**:
   ```bash
   # Verify .env file exists and has OPENAI_API_KEY
   cat .env | grep OPENAI_API_KEY
   ```

2. **Check Initialization**:
   ```python
   from src.codegen.generator import CodeGenerator
   cg = CodeGenerator()
   print(f"LLM available: {cg.use_llm}")
   ```

3. **Check Errors**: Look for error messages in terminal about LLM calls

### LLM Generation Fails

- System automatically falls back to rule-based generation
- Check terminal for error messages
- Verify API key is valid and has credits
- Check network connection

## Performance

- **LLM Mode**: ~2-5 seconds per code generation (depends on API response time)
- **Rule-Based Mode**: <0.1 seconds (instant)

## Cost Considerations

- **gpt-4o-mini**: Very affordable, good quality
- **gpt-4**: Higher cost, better quality
- Each code generation = 1 API call
- Typical prompt size: ~2000-3000 tokens

## Future Enhancements

- Support for other LLM providers (Anthropic, local models)
- Code caching to reduce API calls
- Multi-turn conversation support
- Code optimization suggestions

