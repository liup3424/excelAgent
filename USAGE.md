# Usage Guide

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up API keys (optional, for LLM features):
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Running the Agent

### Command Line Mode

```bash
python main.py --mode cli
```

Then enter your questions interactively:
- "帮我分析各地区销售趋势"
- "Calculate total sales by product"
- "Find top 10 products by revenue"

### WebSocket Mode

```bash
python main.py --mode websocket --port 8000
```

Connect to `ws://localhost:8000/ws` and send:
- Text messages: `{"type": "text", "text": "your question"}`
- Audio messages: `{"type": "audio", "data": "base64_encoded_audio"}`

## Example Questions

### Chinese
- "帮我分析各地区销售趋势" - Analyze sales trends by region
- "计算每个产品的总销售额" - Calculate total sales per product
- "找出销售额最高的前10个产品" - Find top 10 products by sales
- "比较不同地区的平均销售额" - Compare average sales across regions

### English
- "Analyze sales trends by region"
- "Calculate total sales for each product"
- "Find the top 10 products by sales"
- "Compare average sales across regions"

## Architecture

The system processes questions through these stages:

1. **Preprocessing**: Excel files are preprocessed to handle merged cells, multi-level headers
2. **Intent Extraction**: Natural language is parsed to extract analysis intent
3. **Column Mapping**: Entities are mapped to actual Excel columns
4. **Code Generation**: Python code is generated for the analysis
5. **Execution**: Code is executed safely
6. **Lineage Tracking**: Reports which columns were used

## Output

For each question, you'll receive:
- Generated Python code
- Execution results (tables, charts, statistics)
- Data lineage report (which columns were used)

