"""
Example test cases and prompts
"""

# Example questions in Chinese
CHINESE_QUESTIONS = [
    "帮我分析各地区销售趋势",
    "计算每个产品的总销售额",
    "找出销售额最高的前10个产品",
    "比较不同地区的平均销售额",
    "分析月度销售增长情况",
    "统计每个类别的产品数量",
]

# Example questions in English
ENGLISH_QUESTIONS = [
    "Analyze sales trends by region",
    "Calculate total sales for each product",
    "Find the top 10 products by sales",
    "Compare average sales across regions",
    "Analyze monthly sales growth",
    "Count products by category",
]

# Example complex questions
COMPLEX_QUESTIONS = [
    "帮我找出2023年销售额超过100万的地区，并按销售额从高到低排序",
    "分析每个产品类别在过去6个月的平均销售额趋势",
    "比较Q1和Q2的销售数据，找出增长最快的产品",
    "统计各地区销售人员的业绩，显示前5名",
]

def print_examples():
    """Print example questions"""
    print("="*60)
    print("Example Questions - Chinese")
    print("="*60)
    for i, q in enumerate(CHINESE_QUESTIONS, 1):
        print(f"{i}. {q}")
    
    print("\n" + "="*60)
    print("Example Questions - English")
    print("="*60)
    for i, q in enumerate(ENGLISH_QUESTIONS, 1):
        print(f"{i}. {q}")
    
    print("\n" + "="*60)
    print("Complex Example Questions")
    print("="*60)
    for i, q in enumerate(COMPLEX_QUESTIONS, 1):
        print(f"{i}. {q}")

if __name__ == "__main__":
    print_examples()

