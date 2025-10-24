# Function Calling 函数调用演示项目

这是一个完整的函数调用（Function Calling）演示项目，展示了如何与 AI API 服务器通信，并实现工具函数的调用功能。项目采用模块化设计，支持流式和非流式输出，包含完善的日志系统。

## 项目特性

- 支持 OpenAI 格式的函数调用协议
- 支持流式（Stream）和非流式输出模式
- 模块化的代码架构，易于扩展
- 完善的日志系统，支持彩色输出
- 自动处理多轮对话和工具调用迭代
- 内置三个示例工具函数

## 项目结构

```
Function Calling/
├── main.py                      # 主程序入口
├── chat_client.py              # 聊天客户端，处理 API 通信
├── tool_definitions.py         # 工具定义（OpenAI 格式）
├── tools.py                    # 工具函数实现
├── logger.py                   # 日志模块
└── openai-gpt-oss-120b.jinja   # 聊天模板文件
```

## 核心模块说明

### 1. chat_client.py - 聊天客户端

负责与 AI API 服务器的通信，处理工具调用的完整流程：
- 发送请求到 API 服务器
- 解析模型响应
- 执行工具函数
- 处理多轮对话迭代
- 支持流式和非流式输出

### 2. tool_definitions.py - 工具定义

使用 OpenAI 标准格式定义工具函数：
- `get_random_number`: 生成指定范围内的随机整数
- `get_current_time`: 获取当前日期和时间
- `calculate`: 执行基本数学运算（加减乘除）

### 3. tools.py - 工具实现

包含所有工具函数的具体实现逻辑。

### 4. logger.py - 日志系统

提供统一的日志记录功能：
- 支持多种日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 彩色控制台输出
- 文件日志输出
- 单例模式管理

## 安装依赖

项目依赖以下 Python 库：

```bash
pip install requests
```

Python 版本要求：Python 3.6+

## 使用方法

### 基本使用

运行主程序：

```bash
python main.py
```

### 配置 API 服务器

在 `chat_client.py` 中修改 API 地址：

```python
client = ChatClient(
    api_url="http://your-api-server:port/v1/chat/completions",
    model="your-model-name"
)
```

### 自定义工具函数

#### 步骤 1: 在 tools.py 中添加函数实现

```python
def your_function(param1, param2):
    """函数说明"""
    # 实现逻辑
    return result

# 在 AVAILABLE_FUNCTIONS 字典中注册
AVAILABLE_FUNCTIONS = {
    # ... 现有函数
    "your_function": your_function
}
```

#### 步骤 2: 在 tool_definitions.py 中添加工具定义

```python
TOOLS = [
    # ... 现有工具
    {
        "type": "function",
        "function": {
            "name": "your_function",
            "description": "函数功能描述",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "参数1说明"
                    },
                    "param2": {
                        "type": "number",
                        "description": "参数2说明"
                    }
                },
                "required": ["param1", "param2"]
            }
        }
    }
]
```

### 使用示例

```python
from chat_client import ChatClient
from tool_definitions import TOOLS
from logger import setup_default_logger, INFO

# 设置日志
logger = setup_default_logger(level=INFO)

# 准备消息
messages = [
    {
        "role": "user",
        "content": "帮我产生三个随机数"
    }
]

# 创建客户端
client = ChatClient()

# 发起对话（流式输出）
response = client.chat(
    messages=messages,
    tools=TOOLS,
    reasoning_effort="low",
    model_identity="你是一个专业的数学助手",
    stream=True
)

print(f"最终回复: {response}")
```

## API 参数说明

### ChatClient.chat() 方法参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| messages | List[Dict] | 必填 | OpenAI 格式的消息列表 |
| tools | List[Dict] | 必填 | 工具定义列表 |
| max_iterations | int | 5 | 最大对话迭代次数 |
| reasoning_effort | str | "medium" | 推理努力程度（low/medium/high） |
| model_identity | str | None | 可选的模型身份描述 |
| builtin_tools | List[str] | None | 内置工具列表 |
| temperature | float | 0.7 | 温度参数 |
| max_tokens | int | 2000 | 最大 token 数 |
| stream | bool | False | 是否使用流式输出 |

## 工作流程

1. 用户发送消息给 AI
2. AI 分析消息并决定是否需要调用工具
3. 如果需要调用工具，AI 返回工具调用请求
4. 客户端执行工具函数并获取结果
5. 将工具执行结果发送回 AI
6. AI 根据工具结果生成最终回复
7. 返回最终回复给用户

## 日志系统

项目提供了完善的日志功能：

```python
from logger import setup_default_logger, DEBUG

# 创建日志器
logger = setup_default_logger(
    level=DEBUG,
    log_file="logs/app.log",
    enable_color=True
)

# 使用日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

## 注意事项

1. 确保 API 服务器地址正确且可访问
2. 工具函数的参数必须与定义中的参数一致
3. 流式输出模式下会实时显示响应内容
4. 默认最多进行 15 轮对话迭代，可通过 `max_iterations` 参数调整
5. 工具函数执行失败时会返回错误消息给 AI

## 许可证

本项目仅供学习和演示使用。

## 常见问题

### Q: 如何处理工具函数执行错误？

A: 项目会自动捕获错误并将错误信息返回给 AI，AI 可以根据错误信息调整策略或向用户说明。

### Q: 可以同时调用多个工具吗？

A: 可以，AI 可以在一次响应中返回多个工具调用请求，客户端会依次执行。

### Q: 如何调整日志级别？

A: 在创建 logger 时设置 level 参数，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL。

### Q: 流式输出和非流式输出有什么区别？

A: 流式输出会实时显示 AI 的响应内容（逐字输出），非流式输出会等待完整响应后一次性返回。流式输出提供更好的用户体验。

## 贡献

欢迎提交问题和改进建议。

