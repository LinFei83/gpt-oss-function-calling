"""
工具函数模块
包含所有可供 AI 调用的工具函数实现
"""
import random
from datetime import datetime
from tool_decorator import tool, AVAILABLE_FUNCTIONS


@tool()
def get_random_number(min_value: int = 0, max_value: int = 100):
    """
    生成一个指定范围内的随机整数
    
    参数:
        min_value: 随机数的最小值
        max_value: 随机数的最大值
    
    返回:
        随机整数
    """
    return random.randint(min_value, max_value)


@tool()
def get_current_time():
    """
    获取当前的日期和时间
    
    返回:
        当前时间的字符串表示
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool()
def calculate(operation: str, num1: float, num2: float):
    """
    执行基本的数学运算（加、减、乘、除）
    
    参数:
        operation: 运算类型（add, subtract, multiply, divide）
        num1: 第一个数字
        num2: 第二个数字
    
    返回:
        计算结果
    """
    operations_map = {
        "add": lambda: num1 + num2,
        "subtract": lambda: num1 - num2,
        "multiply": lambda: num1 * num2,
        "divide": lambda: num1 / num2 if num2 != 0 else "错误：除数不能为0"
    }
    
    return operations_map.get(operation, lambda: "错误：不支持的运算类型")()


# 导出 AVAILABLE_FUNCTIONS（从 tool_decorator 导入）
__all__ = ['AVAILABLE_FUNCTIONS', 'get_random_number', 'get_current_time', 'calculate']

