"""
工具函数模块
包含所有可供 AI 调用的工具函数实现
"""
import random
import json
from datetime import datetime
from typing import List
from src.tools.decorator import tool, AVAILABLE_FUNCTIONS


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


@tool(name="delegate_task")
def delegate_task(agent_type: str, task_description: str):
    """
    将任务委派给专门的代理（Agent）执行
    
    每个代理都是一个有专门能力的模型，有固定的工具和身份：
    - math_agent: 数学计算代理，可以生成随机数、执行数学运算
    - time_agent: 时间查询代理，可以获取当前时间
    
    参数:
        agent_type: 代理类型（math_agent/time_agent）
        task_description: 任务的详细描述，应该清晰说明需要完成什么任务
    
    返回:
        代理的执行结果
    """
    from src.core.subtask_executor import get_subtask_executor
    
    # 获取子任务执行器并执行
    executor = get_subtask_executor()
    result = executor.execute(
        agent_type=agent_type,
        task_description=task_description
    )
    
    # 返回格式化的结果
    if result["success"]:
        return json.dumps({
            "status": "success",
            "agent": result.get("agent_name", agent_type),
            "result": result["result"],
            "task": task_description
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "error",
            "agent": result.get("agent_name", agent_type),
            "error": result["error"],
            "task": task_description
        }, ensure_ascii=False)


# 导出 AVAILABLE_FUNCTIONS（从 tool_decorator 导入）
__all__ = ['AVAILABLE_FUNCTIONS', 'get_random_number', 'get_current_time', 'calculate', 'delegate_task']

