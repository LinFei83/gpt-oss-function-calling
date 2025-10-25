"""
使用 @tool 装饰器的示例

本示例展示了如何使用 @tool 装饰器来简化工具的注册过程
"""
from src.tools.decorator import tool, AVAILABLE_FUNCTIONS, get_all_tools
from typing import Optional


# 示例 1: 基本用法 - 使用函数名和 docstring
@tool()
def greet_user(name: str, language: str = "zh"):
    """
    向用户打招呼
    
    参数:
        name: 用户的名字
        language: 语言代码（zh表示中文，en表示英文）
    
    返回:
        问候语字符串
    """
    greetings = {
        "zh": f"你好，{name}！",
        "en": f"Hello, {name}!",
    }
    return greetings.get(language, greetings["zh"])


# 示例 2: 自定义名称和描述
@tool(name="add_numbers", description="将两个数字相加并返回结果")
def my_adder(x: float, y: float):
    """
    这个 docstring 会被忽略，因为提供了自定义描述
    
    参数:
        x: 第一个数字
        y: 第二个数字
    
    返回:
        两数之和
    """
    return x + y


# 示例 3: 支持可选参数
@tool()
def search_items(query: str, max_results: int = 10, category: Optional[str] = None):
    """
    搜索项目
    
    参数:
        query: 搜索查询字符串
        max_results: 最大返回结果数
        category: 可选的分类过滤
    
    返回:
        搜索结果列表
    """
    # 这里只是示例，实际应该有搜索逻辑
    return f"搜索 '{query}'，最多 {max_results} 个结果" + (f"，分类：{category}" if category else "")


# 示例 4: 布尔类型参数
@tool()
def format_text(text: str, uppercase: bool = False, add_emoji: bool = False):
    """
    格式化文本
    
    参数:
        text: 要格式化的文本
        uppercase: 是否转换为大写
        add_emoji: 是否添加表情符号
    
    返回:
        格式化后的文本
    """
    result = text.upper() if uppercase else text
    if add_emoji:
        result = f"{result} 😊"
    return result


# 示例 5: 列表类型参数
@tool()
def calculate_average(numbers: list):
    """
    计算数字列表的平均值
    
    参数:
        numbers: 数字列表
    
    返回:
        平均值
    """
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)


if __name__ == "__main__":
    print("=" * 60)
    print("已注册的工具函数:")
    print("=" * 60)
    
    for func_name in AVAILABLE_FUNCTIONS.keys():
        print(f"  - {func_name}")
    
    print("\n" + "=" * 60)
    print("工具定义 (JSON 格式):")
    print("=" * 60)
    
    import json
    all_tools = get_all_tools()
    for tool_def in all_tools:
        print(f"\n工具名称: {tool_def['function']['name']}")
        print(f"描述: {tool_def['function']['description']}")
        print(f"参数: {json.dumps(tool_def['function']['parameters'], indent=2, ensure_ascii=False)}")
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("测试工具调用:")
    print("=" * 60)
    
    # 测试调用
    print(f"\ngreet_user('张三'): {AVAILABLE_FUNCTIONS['greet_user']('张三')}")
    print(f"greet_user('John', 'en'): {AVAILABLE_FUNCTIONS['greet_user']('John', 'en')}")
    print(f"add_numbers(10, 20): {AVAILABLE_FUNCTIONS['add_numbers'](10, 20)}")
    print(f"search_items('手机'): {AVAILABLE_FUNCTIONS['search_items']('手机')}")
    print(f"format_text('hello', uppercase=True): {AVAILABLE_FUNCTIONS['format_text']('hello', uppercase=True)}")

