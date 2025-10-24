"""
工具函数模块
包含所有可供 AI 调用的工具函数实现
"""
import random
from datetime import datetime


def get_random_number(min_value=0, max_value=100):
    """
    生成一个随机数
    
    参数:
        min_value: 最小值（默认为0）
        max_value: 最大值（默认为100）
    
    返回:
        随机整数
    """
    return random.randint(min_value, max_value)


def get_current_time():
    """
    获取当前时间
    
    返回:
        当前时间的字符串表示
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(operation, num1, num2):
    """
    执行简单的数学运算
    
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


# 函数映射表
AVAILABLE_FUNCTIONS = {
    "get_random_number": get_random_number,
    "get_current_time": get_current_time,
    "calculate": calculate
}

