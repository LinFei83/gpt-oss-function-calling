"""
主程序入口
演示如何使用模块化的函数调用系统
支持主-子模型架构，可以将子任务委派给独立的模型执行
"""
from src.core import ChatClient, setup_default_logger, INFO
from src.tools import implementations  # 导入以触发工具注册
from src.tools import initialize_tool_groups, get_tools_for_groups


def example_with_agent_delegation():
    """
    多代理协作示例（推荐）
    
    新架构：主模型 + 专门代理
    1. 主模型只负责任务分析和委派，使用 delegate_task 工具
    2. 专门代理（Agent）处理具体任务：
       - math_agent: 数学计算代理
       - time_agent: 时间查询代理
       - general_agent: 综合工具代理
    3. 每个代理有固定的工具和专门身份
    4. 代理在独立上下文中执行任务，结果返回给主模型
    
    优势：
    - 主模型上下文简洁，只关注任务协调
    - 专门代理各司其职，效率更高
    - 易于扩展新的专门代理
    """
    logger = setup_default_logger(level=INFO)
    logger.info("=" * 80)
    logger.info("多代理协作示例")
    logger.info("=" * 80)
    
    # 初始化工具分组配置
    initialize_tool_groups()
    
    # 获取主模型工具集（只包含任务委派工具）
    coordinator_tools = get_tools_for_groups(['coordinator'])
    
    logger.info(f"主模型使用工具分组: ['coordinator']")
    logger.info(f"主模型可用工具: {[t['function']['name'] for t in coordinator_tools]}")
    logger.info(f"可用的专门代理: math_agent, time_agent, general_agent")
    
    messages = [
        {
            "role": "user",
            "content": """请帮我完成以下任务：
1. 生成三个随机数（范围 1-100）
2. 将这三个数相乘
3. 告诉我当前时间
"""
        }
    ]
    
    # 创建主模型客户端（协调中心）
    client = ChatClient(task_name="协调中心")
    
    # 发起对话
    final_response = client.chat(
        messages=messages,
        tools=coordinator_tools,
        reasoning_effort="medium",
        model_identity="""你是一个任务协调中心（Coordinator）。你的职责是：
1. 分析用户的请求，理解任务目标
2. 识别需要哪些专门代理来完成任务
3. 使用 delegate_task 工具将任务委派给合适的代理：
4. 整合代理的执行结果，向用户报告

重要：你只负责协调，不能直接执行具体任务。所有具体任务必须委派给代理。""",
        stream=True,
        max_iterations=15
    )
    
    logger.info("=" * 80)
    logger.info(f"任务完成!")
    logger.info("=" * 80)


def example_with_custom_params():
    """
    传统模式示例（不使用子任务）
    
    支持的功能：
    1. 流式输出：实时显示模型的回复内容
    2. 思考过程：显示模型的推理思考过程（reasoning_content）
    3. 函数调用：自动调用工具函数并返回结果
    
    推理努力程度说明：
    - low: 快速响应，适合简单任务
    - medium: 平衡响应速度和质量（默认）
    - high: 更深入的思考，适合复杂任务
    """
    logger = setup_default_logger(level=INFO)
    logger.info("=" * 60)
    logger.info("传统模式示例（不使用子任务）")
    logger.info("=" * 60)
    
    # 初始化工具分组配置
    initialize_tool_groups()
    
    # 获取需要的工具分组（可以指定多个分组，会自动去重）
    tools_to_use = get_tools_for_groups(['all'])  
    
    logger.info(f"使用工具分组: ['all']")
    logger.info(f"工具数量: {len(tools_to_use)}")
    
    messages = [
        # {
        #     "role": "system",
        #     "content": "你是一个专业的数学助手，擅长处理各种计算和随机数生成任务, 如果有人询问你的身份你可以回答你是PPO",
        # },
        {
            "role": "user",
            "content": """请帮我完成以下任务：
            1. 生成三个随机数（范围 1-100）
            2. 将这三个数相乘
            3. 告诉我当前时间
            """
        }
    ]
    
    # 创建客户端
    client = ChatClient()
    
    # 发起对话（启用流式输出）
    final_response = client.chat(
        messages=messages, 
        tools=tools_to_use,  # 使用从分组获取的工具
        reasoning_effort="low",
        model_identity="你是一个专业的数学助手，擅长处理各种计算和随机数生成任务",
        stream=True
    )


if __name__ == "__main__":
    print("\n请选择运行模式：")
    print("1. 多代理协作架构（推荐，主模型只负责任务分配）")
    print("2. 传统模式（直接执行）")
    
    choice = input("\n请输入选项 (1-2，默认1): ").strip() or "1"
    
    if choice == "1":
        example_with_agent_delegation()
    elif choice == "2":
        example_with_custom_params()
    else:
        print("无效选项，使用默认模式...")
        example_with_agent_delegation()

