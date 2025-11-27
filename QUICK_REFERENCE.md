# Quick Reference Card

## 🚀 Start the App

```bash
source venv/bin/activate
python app_gradio.py
```

Open: **http://localhost:7860**

## 📝 Basic Workflow

1. **Upload** → Select Excel files → Click "Upload Excel Files"
2. **Ask** → Type question → Click "Run Analysis"  
3. **View** → Check tabs: Code, Tables, Charts, Summary, Lineage

## 💬 Example Questions

### Chinese
- "列出所有数据"
- "分析各地区销售趋势"
- "计算总销售额"
- "找出销售额最高的前10个产品"

### English
- "Show all data"
- "Analyze sales trends by region"
- "Calculate total sales"
- "Find top 10 products by sales"

## ⚙️ Configuration

Create `.env` file:
```
OPENAI_API_KEY=your_key_here
```

## 📁 Where Files Go

- **Uploaded files**: `workspace/uploads/`
- **Processed tables**: `workspace/data/`
- **Charts**: `workspace/charts/`

## 🆘 Common Issues

- **App won't start**: Check port 7860, run `pip install -r requirements.txt`
- **Upload fails**: Check file format (.xlsx or .xls)
- **No results**: Upload files first, wait for processing
- **Analysis fails**: Check Summary tab for errors

## 📚 More Help

- Full guide: [HOW_TO_USE.md](HOW_TO_USE.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Gradio details: [GRADIO_README.md](GRADIO_README.md)

