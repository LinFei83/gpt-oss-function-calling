# Function Calling 函数调用演示项目

这是一个完整的函数调用（Function Calling）演示项目，展示了如何与 AI API 服务器通信，并实现工具函数的调用功能。项目采用模块化设计，支持流式和非流式输出，包含完善的日志系统。

## 项目特性

- 支持 OpenAI 格式的函数调用协议
- 支持流式（Stream）和非流式输出模式
- 模块化的代码架构，易于扩展
- 完善的日志系统，支持彩色输出
- 自动处理多轮对话和工具调用迭代
- 内置三个示例工具函数
- 提供 `@tool` 装饰器，自动生成工具定义和注册

## 项目结构

```
Function Calling/
├── src/                        # 源代码目录
│   ├── __init__.py
│   ├── core/                   # 核心功能模块
│   │   ├── __init__.py
│   │   ├── chat_client.py      # 聊天客户端，处理 API 通信
│   │   └── logger.py           # 日志系统
│   │
│   └── tools/                  # 工具相关模块
│       ├── __init__.py
│       ├── decorator.py        # 工具装饰器
│       ├── implementations.py  # 工具函数实现
│       └── groups.py           # 工具分组管理
│
├── examples/                   # 示例代码
│   ├── __init__.py
│   ├── basic_usage.py          # 基本使用示例
│   ├── multi_turn.py           # 多轮对话示例
│   └── tool_usage.py           # 装饰器使用示例
│
├── config/                     # 配置文件
│   └── tool_groups.yaml        # 工具分组配置
│
├── templates/                  # 模板文件
│   └── openai-gpt-oss-120b.jinja
│
├── requirements.txt            # 项目依赖
└── README.md                   # 项目说明文档
```

## 核心模块说明

### 1. src/core/chat_client.py - 聊天客户端

负责与 AI API 服务器的通信，处理工具调用的完整流程：
- 发送请求到 API 服务器
- 解析模型响应
- 执行工具函数
- 处理多轮对话迭代
- 支持流式和非流式输出

### 2. src/tools/decorator.py - 工具装饰器

提供 `@tool` 装饰器，自动化工具注册过程：
- 自动从类型注解生成 JSON Schema 参数定义
- 从 docstring 提取工具和参数描述
- 支持自定义工具名称和描述
- 自动识别必需参数和可选参数
- 维护 `AVAILABLE_FUNCTIONS` 和 `TOOLS` 注册表

### 3. src/tools/implementations.py - 工具实现

包含所有工具函数的具体实现逻辑：
- `get_random_number`: 生成指定范围内的随机整数
- `get_current_time`: 获取当前日期和时间
- `calculate`: 执行基本数学运算（加减乘除）

使用 `@tool` 装饰器自动注册。

### 4. src/tools/groups.py - 工具分组管理

负责加载和管理工具分组配置，支持从 YAML 文件加载分组定义。

### 5. src/core/logger.py - 日志系统

提供统一的日志记录功能：
- 支持多种日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- 彩色控制台输出
- 文件日志输出
- 单例模式管理

## 安装依赖

项目依赖以下 Python 库：

```bash
pip install -r requirements.txt
```

Python 版本要求：Python 3.7+

## 使用方法

### 基本使用

运行主程序（单次对话示例）：

```bash
python -m examples.basic_usage
```

### 多轮对话示例

运行多轮对话程序，实现持续交互：

```bash
python -m examples.multi_turn
```

多轮对话系统支持以下功能：

- 持续对话：可以连续提问，系统会保持对话上下文
- 对话历史管理：自动记录所有对话内容
- 命令支持：
  - `/help` - 显示帮助信息
  - `/history` - 查看完整对话历史
  - `/clear` - 清空对话历史，开始新对话
  - `/save` - 将对话历史保存到JSON文件
  - `/exit` - 退出程序

示例对话：

```
你: 帮我生成两个随机数
助手: [调用工具生成随机数...]
      好的，我生成了两个随机数：45 和 78

你: 把它们相加
助手: [调用计算工具...]
      45 + 78 = 123

你: /history
[显示完整对话历史...]

你: /exit
感谢使用，再见！
```

### 配置 API 服务器

在 `src/core/chat_client.py` 中修改 API 地址：

```python
client = ChatClient(
    api_url="http://your-api-server:port/v1/chat/completions",
    model="your-model-name"
)
```

### 自定义工具函数

项目支持两种方式添加工具函数：使用 `@tool` 装饰器（推荐）或手动注册。

#### 方法 1: 使用 @tool 装饰器（推荐）

使用 `@tool` 装饰器可以自动完成工具注册和定义生成，大大简化开发流程：

```python
from src.tools.decorator import tool

@tool()
def your_function(param1: str, param2: int = 0):
    """
    函数功能描述
    
    参数:
        param1: 参数1说明
        param2: 参数2说明
    
    返回:
        返回值说明
    """
    # 实现逻辑
    return result
```

装饰器会自动：
- 从函数名生成工具名称
- 从 docstring 提取工具描述和参数说明
- 从类型注解自动推断参数类型（支持 `int`, `float`, `str`, `bool`, `list`, `dict`）
- 识别必需参数和可选参数（有默认值的参数为可选）
- 注册函数到 `AVAILABLE_FUNCTIONS`
- 生成工具定义到 `TOOLS`

支持的类型注解：
- `int` → JSON Schema `integer`
- `float` → JSON Schema `number`
- `str` → JSON Schema `string`
- `bool` → JSON Schema `boolean`
- `list` → JSON Schema `array`
- `dict` → JSON Schema `object`
- `Optional[T]` 会被正确处理为可选参数

自定义工具名称和描述：

```python
@tool(name="custom_name", description="自定义描述")
def my_function(x: float):
    """这个 docstring 会被忽略"""
    return x * 2
```

完整示例请参考 `examples/tool_usage.py`。

#### 方法 2: 手动注册（传统方式）

如果需要更精细的控制，可以手动注册工具：

**步骤 1: 在 src/tools/implementations.py 中添加函数实现**

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

**步骤 2: 使用 @tool 装饰器注册（推荐）**

```python
from src.tools.decorator import tool

@tool()
def your_function(param1: str, param2: float):
    """
    函数功能描述
    
    参数:
        param1: 参数1说明
        param2: 参数2说明
    """
    # 实现逻辑
    return result
```

### 使用示例

```python
from src.core import ChatClient, setup_default_logger, INFO
from src.tools import get_all_tools

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
    tools=get_all_tools(),
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
from src.core import setup_default_logger, DEBUG

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

