"""
主程序入口
演示如何使用模块化的函数调用系统
"""
from chat_client import ChatClient
from tool_definitions import TOOLS
from logger import setup_default_logger, INFO


def example_with_custom_params():
    """使用自定义参数的示例（流式输出）"""
    logger = setup_default_logger(level=INFO)
    logger.info("=" * 60)
    logger.info("自定义参数示例（流式输出）")
    logger.info("=" * 60)
    
    messages = [
        {
            "role": "user",
            "content": "帮我产生十个随机数"
        }
    ]
    
    # 创建客户端
    client = ChatClient()
    
    # 发起对话（启用流式输出）
    final_response = client.chat(
        messages=messages, 
        tools=TOOLS,
        reasoning_effort="low",
        model_identity="你是一个专业的数学助手，擅长处理各种计算和随机数生成任务",
        stream=True
    )
    
    if final_response:
        logger.info(f"最终回复: {final_response}")


if __name__ == "__main__":
    example_with_custom_params()

