"""
工具分组管理模块
负责加载和管理工具分组配置
"""
import yaml
import os
from typing import List


DEFAULT_CONFIG_PATH = "config/tool_groups.yaml"


def load_groups_from_yaml(config_path: str = DEFAULT_CONFIG_PATH) -> dict:
    """
    从 YAML 配置文件加载工具分组
    
    参数:
        config_path: 配置文件路径
    
    返回:
        分组配置字典，格式为 {分组名: [工具名列表]}
    
    异常:
        FileNotFoundError: 配置文件不存在
        yaml.YAMLError: YAML 格式错误
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            groups_config = yaml.safe_load(f)
        
        if not isinstance(groups_config, dict):
            raise ValueError("配置文件格式错误：根元素必须是字典")
        
        # 验证配置格式
        for group_name, tool_names in groups_config.items():
            if not isinstance(tool_names, list):
                raise ValueError(f"分组 '{group_name}' 的值必须是列表")
        
        return groups_config
    
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"YAML 解析错误: {e}")


def initialize_tool_groups(config_path: str = DEFAULT_CONFIG_PATH):
    """
    初始化工具分组系统
    从配置文件加载分组并注册到 tool_decorator
    
    参数:
        config_path: 配置文件路径
    """
    from src.tools.decorator import load_tool_groups
    
    groups_config = load_groups_from_yaml(config_path)
    load_tool_groups(groups_config)
    
    return groups_config


def get_tools_for_groups(group_names: List[str]) -> List[dict]:
    """
    获取指定分组的工具定义列表
    
    参数:
        group_names: 分组名称列表，可以是单个或多个分组
    
    返回:
        工具定义列表（OpenAI 格式），自动去重
    """
    from src.tools.decorator import get_tools_by_groups
    return get_tools_by_groups(group_names)


def validate_groups(group_names: List[str]) -> tuple:
    """
    验证分组名称是否存在
    
    参数:
        group_names: 要验证的分组名称列表
    
    返回:
        (valid_groups, invalid_groups) 元组
    """
    from src.tools.decorator import get_available_groups
    
    available_groups = get_available_groups()
    valid_groups = [g for g in group_names if g in available_groups]
    invalid_groups = [g for g in group_names if g not in available_groups]
    
    return valid_groups, invalid_groups


if __name__ == "__main__":
    from src.tools import implementations  # 导入以注册工具
    
    print("=" * 60)
    print("工具分组系统测试")
    print("=" * 60)
    
    # 初始化分组配置
    try:
        groups_config = initialize_tool_groups()
        print(f"\n成功加载配置文件")
        print(f"可用分组: {list(groups_config.keys())}")
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        exit(1)
    
    # 显示各分组的工具
    print("\n" + "=" * 60)
    print("分组详情:")
    print("=" * 60)
    for group_name, tool_names in groups_config.items():
        print(f"\n[{group_name}]")
        for tool_name in tool_names:
            print(f"  - {tool_name}")
    
    # 测试获取单个分组的工具
    print("\n" + "=" * 60)
    print("测试获取单个分组 'math':")
    print("=" * 60)
    math_tools = get_tools_for_groups(['math'])
    for tool in math_tools:
        print(f"  - {tool['function']['name']}: {tool['function']['description']}")
    
    # 测试获取多个分组的工具（自动去重）
    print("\n" + "=" * 60)
    print("测试获取多个分组 ['math', 'time']（自动去重）:")
    print("=" * 60)
    combined_tools = get_tools_for_groups(['math', 'time'])
    for tool in combined_tools:
        print(f"  - {tool['function']['name']}: {tool['function']['description']}")
    
    # 测试分组验证
    print("\n" + "=" * 60)
    print("测试分组验证:")
    print("=" * 60)
    test_groups = ['math', 'invalid_group', 'time', 'nonexistent']
    valid, invalid = validate_groups(test_groups)
    print(f"有效分组: {valid}")
    print(f"无效分组: {invalid}")

