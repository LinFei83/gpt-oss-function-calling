"""
多轮对话示例
演示如何实现持续的对话交互，保持对话历史，并支持多种命令
"""
from src.core import ChatClient, setup_default_logger, INFO
from src.tools import implementations  # 导入以触发工具注册
from src.tools import initialize_tool_groups, get_tools_for_groups
import json


class MultiTurnChat:
    """多轮对话管理器"""
    
    def __init__(self, stream=True, reasoning_effort="low", tool_groups=None):
        """
        初始化多轮对话管理器
        
        参数:
            stream: 是否使用流式输出
            reasoning_effort: 推理努力程度（low/medium/high）
            tool_groups: 要使用的工具分组列表，默认使用 ['all']
        """
        self.logger = setup_default_logger(level=INFO)
        self.client = ChatClient()
        self.messages = []
        self.stream = stream
        self.reasoning_effort = reasoning_effort
        self.running = True
        
        # 初始化工具分组配置
        initialize_tool_groups()
        
        # 获取要使用的工具
        if tool_groups is None:
            tool_groups = ['all']
        self.tools = get_tools_for_groups(tool_groups)
        self.tool_groups = tool_groups
        
    def add_user_message(self, content: str):
        """添加用户消息到对话历史"""
        self.messages.append({
            "role": "user",
            "content": content
        })
    
    def display_welcome(self):
        """显示欢迎信息和使用说明"""
        print("\n" + "=" * 60)
        print("欢迎使用多轮对话系统")
        print("=" * 60)
        print(f"\n使用工具分组: {self.tool_groups}")
        print(f"可用工具数量: {len(self.tools)}")
        print("\n可用命令：")
        print("  /help     - 显示帮助信息")
        print("  /history  - 显示对话历史")
        print("  /clear    - 清空对话历史")
        print("  /save     - 保存对话历史到文件")
        print("  /exit     - 退出程序")
        print("\n直接输入文字即可开始对话")
        print("=" * 60 + "\n")
    
    def display_help(self):
        """显示帮助信息"""
        print("\n" + "-" * 60)
        print("帮助信息")
        print("-" * 60)
        print("这是一个支持函数调用的多轮对话系统。")
        print("\n可用的工具函数：")
        print("  1. get_random_number - 生成随机数")
        print("  2. get_current_time  - 获取当前时间")
        print("  3. calculate         - 执行数学运算（加减乘除）")

    def display_history(self):
        """显示对话历史"""
        if not self.messages:
            print("\n对话历史为空\n")
            return
        
        print("\n" + "-" * 60)
        print(f"对话历史（共 {len(self.messages)} 条消息）")
        print("-" * 60)
        
        for i, msg in enumerate(self.messages, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # 根据角色设置显示格式
            if role == "user":
                print(f"\n[{i}] 用户:")
                print(f"  {content}")
            elif role == "assistant":
                print(f"\n[{i}] 助手:")
                if content:
                    print(f"  {content}")
                # 显示工具调用信息
                if "tool_calls" in msg:
                    print("  [调用了工具函数]")
            elif role == "tool":
                print(f"\n[{i}] 工具结果 ({msg.get('name', 'unknown')}):")
                print(f"  {content}")
        
        print("-" * 60 + "\n")
    
    def clear_history(self):
        """清空对话历史"""
        self.messages = []
        print("\n对话历史已清空\n")
    
    def save_history(self, filename="chat_history.json"):
        """保存对话历史到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
            print(f"\n对话历史已保存到: {filename}\n")
        except Exception as e:
            print(f"\n保存失败: {e}\n")
    
    def handle_command(self, user_input: str) -> bool:
        """
        处理命令
        
        返回:
            True 表示已处理命令，False 表示不是命令
        """
        if not user_input.startswith('/'):
            return False
        
        command = user_input.lower().strip()
        
        if command == '/help':
            self.display_help()
        elif command == '/history':
            self.display_history()
        elif command == '/clear':
            self.clear_history()
        elif command == '/save':
            self.save_history()
        elif command == '/exit':
            self.running = False
            print("\n感谢使用，再见！\n")
        else:
            print(f"\n未知命令: {command}")
            print("输入 /help 查看帮助信息\n")
        
        return True
    
    def chat_once(self, user_input: str):
        """执行一次对话"""
        # 添加用户消息
        self.add_user_message(user_input)
        
        # 发送请求并获取响应
        response = self.client.chat(
            messages=self.messages,
            tools=self.tools,  # 使用初始化时配置的工具
            reasoning_effort=self.reasoning_effort,
            model_identity="你是一个友好的AI助手，可以使用各种工具来帮助用户解决问题。",
            stream=self.stream
        )
        
        # 注意：client.chat 内部使用 messages.copy()，不会修改原始 messages
        # 但它返回的 response 只是最终的文本内容，我们需要手动添加助手消息
        # 实际上，为了保持完整的对话历史（包括工具调用），我们需要改进这个逻辑
        
        if response:
            # 添加助手的响应到历史中
            self.messages.append({
                "role": "assistant",
                "content": response
            })
        else:
            self.logger.warning("未获取到有效响应")
    
    def run(self):
        """运行多轮对话"""
        self.display_welcome()
        
        while self.running:
            try:
                # 获取用户输入
                user_input = input("你: ").strip()
                
                # 跳过空输入
                if not user_input:
                    continue
                
                # 处理命令
                if self.handle_command(user_input):
                    continue
                
                # 执行对话
                print()  # 换行
                self.chat_once(user_input)
                print()  # 对话结束后换行
                
            except KeyboardInterrupt:
                print("\n\n检测到中断信号...")
                self.running = False
                print("感谢使用，再见！\n")
            except Exception as e:
                self.logger.error(f"发生错误: {e}")
                print(f"\n发生错误: {e}\n")


def main():
    """主函数"""
    # 创建多轮对话管理器
    # stream=True: 启用流式输出，实时显示AI回复
    # reasoning_effort: 设置推理深度
    #   - "low": 快速响应
    #   - "medium": 平衡速度和质量
    #   - "high": 深度思考
    chat = MultiTurnChat(stream=True, reasoning_effort="low")
    
    # 运行对话
    chat.run()


if __name__ == "__main__":
    main()

