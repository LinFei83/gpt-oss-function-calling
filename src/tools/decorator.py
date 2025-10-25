"""
工具装饰器模块
提供 @tool 装饰器来自动注册工具函数和生成工具定义
支持工具分组功能，可以按需组合不同的工具集
"""
import inspect
from typing import get_type_hints, get_origin, get_args, Union, List


# 存储注册的工具函数和定义
AVAILABLE_FUNCTIONS = {}
# 存储所有工具定义的字典，key 为工具名称
_TOOLS_REGISTRY = {}
# 存储工具分组信息，key 为分组名称，value 为工具名称列表
_TOOL_GROUPS = {}


def _python_type_to_json_type(py_type):
    """
    将 Python 类型转换为 JSON Schema 类型
    
    参数:
        py_type: Python 类型注解
    
    返回:
        JSON Schema 类型字符串
    """
    # 处理 Union 类型（例如 Optional[str] 等同于 Union[str, None]）
    origin = get_origin(py_type)
    if origin is Union:
        args = get_args(py_type)
        # 过滤掉 NoneType
        non_none_types = [arg for arg in args if arg is not type(None)]
        if len(non_none_types) == 1:
            py_type = non_none_types[0]
    
    # 基本类型映射
    type_mapping = {
        int: "integer",
        float: "number",
        str: "string",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    
    # 检查是否是基本类型
    for python_type, json_type in type_mapping.items():
        if py_type is python_type or py_type == python_type:
            return json_type
    
    # 默认返回 string
    return "string"


def _extract_param_description(docstring, param_name):
    """
    从 docstring 中提取参数描述
    
    参数:
        docstring: 函数的文档字符串
        param_name: 参数名称
    
    返回:
        参数描述字符串，如果未找到则返回空字符串
    """
    if not docstring:
        return ""
    
    lines = docstring.split('\n')
    in_params_section = False
    
    for line in lines:
        stripped = line.strip()
        
        # 检测参数部分开始
        if stripped.lower().startswith('参数:') or stripped.lower().startswith('args:') or stripped.lower().startswith('parameters:'):
            in_params_section = True
            continue
        
        # 检测参数部分结束
        if in_params_section and (stripped.lower().startswith('返回:') or stripped.lower().startswith('return:') or stripped.lower().startswith('raises:')):
            break
        
        # 在参数部分中查找参数描述
        if in_params_section and param_name in stripped:
            # 提取参数描述（去除参数名和冒号后的内容）
            if ':' in stripped:
                parts = stripped.split(':', 1)
                if param_name in parts[0]:
                    return parts[1].strip()
    
    return f"{param_name} 参数"


def _extract_function_description(docstring):
    """
    从 docstring 中提取函数描述（第一行或第一段）
    
    参数:
        docstring: 函数的文档字符串
    
    返回:
        函数描述字符串
    """
    if not docstring:
        return "无描述"
    
    lines = docstring.strip().split('\n')
    description_lines = []
    
    for line in lines:
        stripped = line.strip()
        # 遇到参数或返回值部分就停止
        if stripped.lower().startswith(('参数:', 'args:', 'parameters:', '返回:', 'return:', 'raises:')):
            break
        if stripped:
            description_lines.append(stripped)
    
    return ' '.join(description_lines) if description_lines else "无描述"


def tool(name=None, description=None):
    """
    工具装饰器，用于自动注册函数为工具并生成工具定义
    
    使用示例:
        @tool()
        def my_function(param1: str, param2: int = 0):
            '''函数描述'''
            pass
        
        @tool(name="custom_name", description="自定义描述")
        def another_function(x: float):
            pass
    
    参数:
        name: 自定义工具名称，如果不提供则使用函数名
        description: 自定义工具描述，如果不提供则从 docstring 提取
    
    返回:
        装饰器函数
    """
    def decorator(func):
        # 确定工具名称
        tool_name = name if name else func.__name__
        
        # 获取函数签名
        sig = inspect.signature(func)
        
        # 获取类型注解
        try:
            type_hints = get_type_hints(func)
        except:
            type_hints = {}
        
        # 提取函数描述
        func_description = description if description else _extract_function_description(func.__doc__)
        
        # 构建参数定义
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            # 获取参数类型
            param_type = type_hints.get(param_name, str)
            json_type = _python_type_to_json_type(param_type)
            
            # 获取参数描述
            param_description = _extract_param_description(func.__doc__, param_name)
            
            # 构建参数定义
            param_def = {
                "type": json_type,
                "description": param_description
            }
            
            # 如果有默认值，添加到定义中
            if param.default != inspect.Parameter.empty:
                param_def["default"] = param.default
            else:
                # 没有默认值的参数是必需的
                required.append(param_name)
            
            properties[param_name] = param_def
        
        # 构建工具定义
        tool_definition = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": func_description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }
        
        # 注册函数
        AVAILABLE_FUNCTIONS[tool_name] = func
        
        # 添加工具定义到注册表（使用工具名作为 key）
        _TOOLS_REGISTRY[tool_name] = tool_definition
        
        return func
    
    return decorator


def get_tools_by_groups(group_names: List[str]) -> List[dict]:
    """
    根据分组名称获取工具定义列表，自动去重
    
    参数:
        group_names: 分组名称列表
    
    返回:
        工具定义列表（OpenAI 格式）
    """
    tool_names = set()
    
    # 收集所有分组中的工具名称（自动去重）
    for group_name in group_names:
        if group_name in _TOOL_GROUPS:
            tool_names.update(_TOOL_GROUPS[group_name])
    
    # 根据工具名称获取工具定义
    tools = []
    for tool_name in tool_names:
        if tool_name in _TOOLS_REGISTRY:
            tools.append(_TOOLS_REGISTRY[tool_name])
    
    return tools


def get_all_tools() -> List[dict]:
    """
    获取所有已注册的工具定义
    
    返回:
        工具定义列表（OpenAI 格式）
    """
    return list(_TOOLS_REGISTRY.values())


def load_tool_groups(groups_config: dict):
    """
    加载工具分组配置
    
    参数:
        groups_config: 分组配置字典，格式为 {分组名: [工具名列表]}
    """
    global _TOOL_GROUPS
    _TOOL_GROUPS = groups_config


def get_available_groups() -> List[str]:
    """
    获取所有可用的分组名称
    
    返回:
        分组名称列表
    """
    return list(_TOOL_GROUPS.keys())


def get_tools_registry() -> dict:
    """
    获取工具注册表（用于调试）
    
    返回:
        工具注册表字典，key 为工具名，value 为工具定义
    """
    return _TOOLS_REGISTRY.copy()

