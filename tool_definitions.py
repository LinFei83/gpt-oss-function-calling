"""
工具定义模块
包含 OpenAI 格式的工具规范定义
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_random_number",
            "description": "生成一个指定范围内的随机整数",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_value": {
                        "type": "number",
                        "description": "随机数的最小值",
                        "default": 0
                    },
                    "max_value": {
                        "type": "number",
                        "description": "随机数的最大值",
                        "default": 100
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行基本的数学运算（加、减、乘、除）",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "description": "运算类型",
                        "enum": ["add", "subtract", "multiply", "divide"]
                    },
                    "num1": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "num2": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                },
                "required": ["operation", "num1", "num2"]
            }
        }
    }
]

