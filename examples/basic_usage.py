"""
主程序入口
演示如何使用模块化的函数调用系统
"""
from src.core import ChatClient, setup_default_logger, INFO
from src.tools import implementations  # 导入以触发工具注册
from src.tools import initialize_tool_groups, get_tools_for_groups


def example_with_custom_params():
    """
    使用自定义参数的示例（流式输出）
    
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
    logger.info("自定义参数示例（流式输出）")
    logger.info("=" * 60)
    
    # 初始化工具分组配置
    initialize_tool_groups()
    
    # 获取需要的工具分组（可以指定多个分组，会自动去重）
    tools_to_use = get_tools_for_groups(['math'])  # 使用数学工具分组
    
    logger.info(f"使用工具分组: ['math']")
    logger.info(f"工具数量: {len(tools_to_use)}")
    
    messages = [
        {
            "role": "user",
            "content": "帮我产生三个随机数, 随后将他们相乘"
        }
    ]
    
    # 创建客户端
    client = ChatClient()
    
    # 发起对话（启用流式输出）
    # 注意：
    # 1. 如果模型有思考过程，会先显示 [思考过程]，然后显示 [实际回复]
    # 2. reasoning_effort 参数控制模型的思考深度：
    #    - "low": 快速响应，可能没有明显的思考过程
    #    - "medium": 适度思考
    #    - "high": 深度思考，会有更详细的推理过程
    final_response = client.chat(
        messages=messages, 
        tools=tools_to_use,  # 使用从分组获取的工具
        reasoning_effort="low", # low, medium, high - 可以改为 "high" 查看更多思考内容
        model_identity="你是一个专业的数学助手，擅长处理各种计算和随机数生成任务",
        stream=True
    )
    
    # 如果需要查看最终回复内容，可以取消下面的注释
    # if final_response:
    #     logger.info(f"最终回复: {final_response}")


if __name__ == "__main__":
    example_with_custom_params()

