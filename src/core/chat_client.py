"""
聊天客户端模块
负责与 AI API 服务器通信和工具调用处理
"""
import json
import requests
from typing import List, Dict, Optional, Any

from src.tools import AVAILABLE_FUNCTIONS
from src.core.logger import Logger


class ChatClient:
    """聊天 API 客户端"""
    
    def __init__(self, api_url: str = "http://192.168.0.19:8974/v1/chat/completions", 
                 model: str = "gpt-oss-120b",
                 task_name: str = "主任务"):
        """
        初始化客户端
        
        参数:
            api_url: API 服务器地址
            model: 模型名称
            task_name: 任务名称，用于日志标识（如"主任务"、"数学代理"等）
        """
        self.api_url = api_url
        self.model = model
        self.task_name = task_name
        self.logger = Logger.get_logger("ChatClient")
    
    def chat(self, messages: List[Dict], tools: List[Dict], 
             max_iterations: int = 15, 
             reasoning_effort: str = "medium",
             model_identity: Optional[str] = None,
             builtin_tools: Optional[List[str]] = None,
             temperature: float = 0.7,
             max_tokens: int = 2000,
             stream: bool = False) -> Optional[str]:
        """
        与 AI 进行对话，支持工具调用
        
        参数:
            messages: OpenAI 格式的消息列表
            tools: OpenAI 格式的工具定义列表
            max_iterations: 最大迭代次数
            reasoning_effort: 推理努力程度（low/medium/high）
            model_identity: 可选的模型身份描述
            builtin_tools: 内置工具列表（如 browser, python）
            temperature: 温度参数
            max_tokens: 最大 token 数
            stream: 是否使用流式输出
        
        返回:
            最终的助手响应内容
        """
        current_messages = messages.copy()
        
        for iteration in range(max_iterations):
            self._print_iteration_header(iteration + 1)
            
            # 构建请求
            payload = self._build_payload(
                current_messages, tools, temperature, max_tokens,
                reasoning_effort, model_identity, builtin_tools, stream
            )
            
            # 发送请求并获取响应
            if stream:
                result = self._send_stream_request(payload, current_messages, tools)
            else:
                result = self._send_request(payload, current_messages, tools)
            
            if not result:
                return None
            
            # 处理响应
            message = self._extract_message(result)
            if not message:
                return None
            
            current_messages.append(message)
            
            # 检查工具调用
            if self._has_tool_calls(message):
                self._process_tool_calls(message, current_messages, iteration)
                self.logger.info("继续下一轮以获取最终响应...")
                continue
            
            # 返回最终内容
            if "content" in message and message["content"]:
                self.logger.info(f"内容: {message['content']}")
                return message["content"]
            
            # 异常情况
            self.logger.warning("响应中既没有工具调用也没有内容")
            self.logger.debug(f"完整消息: {json.dumps(message, ensure_ascii=False, indent=2)}")
            return None
        
        self.logger.warning("达到最大迭代次数")
        return None
    
    def _build_payload(self, messages: List[Dict], tools: List[Dict],
                      temperature: float, max_tokens: int,
                      reasoning_effort: str, model_identity: Optional[str],
                      builtin_tools: Optional[List[str]], stream: bool = False) -> Dict[str, Any]:
        """构建请求 payload"""
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        # 构建 chat_template_kwargs
        chat_template_kwargs = {"reasoning_effort": reasoning_effort}
        
        if model_identity:
            chat_template_kwargs["model_identity"] = model_identity
        
        if builtin_tools:
            chat_template_kwargs["builtin_tools"] = builtin_tools
        
        payload["chat_template_kwargs"] = chat_template_kwargs
        return payload
    
    def _send_request(self, payload: Dict, messages: List[Dict], 
                     tools: List[Dict]) -> Optional[Dict]:
        """发送 HTTP 请求"""
        self.logger.info("发送请求到服务器（标准 OpenAI 格式）...")
        self.logger.info(f"消息数量: {len(messages)}")
        self.logger.info(f"工具数量: {len(tools)}")
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"请求失败: {e}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"错误详情: {e.response.text}")
            return None
    
    def _send_stream_request(self, payload: Dict, messages: List[Dict], 
                           tools: List[Dict]) -> Optional[Dict]:
        """发送流式 HTTP 请求"""
        self.logger.debug(f"Payload: {payload}")
        self.logger.info("发送流式请求到服务器（标准 OpenAI 格式）...")
        self.logger.info(f"消息数量: {len(messages)}")
        self.logger.info(f"工具数量: {len(tools)}")
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=120, stream=True)
            response.raise_for_status()
            
            # 收集完整响应
            full_content = ""
            full_reasoning_content = ""
            full_message = {"role": "assistant", "content": ""}
            tool_calls_data = []
            has_reasoning = False
            
            self.logger.info("流式输出:")
            self.logger.info("-" * 60)
            
            for line in response.iter_lines():
                if not line:
                    continue
                    
                line = line.decode('utf-8')
                
                # 跳过非数据行
                if not line.startswith('data: '):
                    continue
                
                # 提取数据
                data_str = line[6:]  # 去掉 'data: ' 前缀
                
                # 检查是否是结束标记
                if data_str.strip() == '[DONE]':
                    break
                
                try:
                    chunk = json.loads(data_str)
                    
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        
                        # 处理思考内容（reasoning_content）
                        if "reasoning_content" in delta and delta["reasoning_content"]:
                            reasoning_piece = delta["reasoning_content"]
                            full_reasoning_content += reasoning_piece
                            if not has_reasoning:
                                print("[思考过程]:\n", flush=True)
                                has_reasoning = True
                            print(reasoning_piece, end='', flush=True)
                        
                        # 处理内容增量
                        if "content" in delta and delta["content"]:
                            content_piece = delta["content"]
                            full_content += content_piece
                            if has_reasoning and full_reasoning_content:
                                print("\n\n[实际回复]:\n", flush=True)
                                has_reasoning = False  # 防止重复打印标题
                            print(content_piece, end='', flush=True)
                        
                        # 处理工具调用
                        if "tool_calls" in delta:
                            for tool_call_delta in delta["tool_calls"]:
                                index = tool_call_delta.get("index", 0)
                                
                                # 确保 tool_calls_data 有足够的空间
                                while len(tool_calls_data) <= index:
                                    tool_calls_data.append({
                                        "id": "",
                                        "type": "function",
                                        "function": {"name": "", "arguments": ""}
                                    })
                                
                                # 更新工具调用数据
                                if "id" in tool_call_delta:
                                    tool_calls_data[index]["id"] = tool_call_delta["id"]
                                
                                if "function" in tool_call_delta:
                                    func_delta = tool_call_delta["function"]
                                    if "name" in func_delta:
                                        tool_calls_data[index]["function"]["name"] = func_delta["name"]
                                    if "arguments" in func_delta:
                                        tool_calls_data[index]["function"]["arguments"] += func_delta["arguments"]
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"解析流式数据失败: {e}")
                    continue
            
            print("\n", flush=True)  # 确保最后换行
            self.logger.info("-" * 60)
            
            # 构建完整的响应消息
            if full_content:
                full_message["content"] = full_content
            
            if full_reasoning_content:
                full_message["reasoning_content"] = full_reasoning_content
            
            if tool_calls_data:
                full_message["tool_calls"] = tool_calls_data
            
            # 构建符合 OpenAI 格式的响应
            result = {
                "choices": [{
                    "message": full_message,
                    "finish_reason": "stop"
                }]
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"流式请求失败: {e}")
            if hasattr(e.response, 'text'):
                self.logger.error(f"错误详情: {e.response.text}")
            return None
    
    def _extract_message(self, result: Dict) -> Optional[Dict]:
        """从响应中提取消息"""
        if "choices" not in result or len(result["choices"]) == 0:
            self.logger.error("未收到有效响应")
            self.logger.debug(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return None
        
        message = result["choices"][0]["message"]
        self.logger.info("模型响应:")
        self.logger.info(f"角色: {message.get('role')}")
        
        # # 显示思考内容（如果有）
        # if "reasoning_content" in message and message["reasoning_content"]:
        #     self.logger.info("=" * 60)
        #     self.logger.info("[思考过程]:")
        #     self.logger.info(message["reasoning_content"])
        #     self.logger.info("=" * 60)
        
        return message
    
    def _has_tool_calls(self, message: Dict) -> bool:
        """检查消息是否包含工具调用"""
        return "tool_calls" in message and message["tool_calls"]
    
    def _process_tool_calls(self, message: Dict, current_messages: List[Dict], 
                           iteration: int):
        """处理工具调用"""
        tool_calls = message["tool_calls"]
        self.logger.info(f"检测到工具调用: {len(tool_calls)} 个")
        
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            function_args_str = tool_call["function"]["arguments"]
            tool_call_id = tool_call.get("id", f"call_{iteration}")
            
            self._print_tool_call_info(tool_call_id, function_name, function_args_str)
            
            try:
                function_args = json.loads(function_args_str)
                tool_message = self._execute_function(
                    function_name, function_args, tool_call_id
                )
                current_messages.append(tool_message)
            except json.JSONDecodeError as e:
                self.logger.error(f"错误: 解析参数失败 - {e}")
                tool_message = self._create_error_message(
                    tool_call_id, function_name, "参数格式错误"
                )
                current_messages.append(tool_message)
    
    def _execute_function(self, function_name: str, function_args: Dict, 
                         tool_call_id: str) -> Dict:
        """执行工具函数"""
        if function_name in AVAILABLE_FUNCTIONS:
            function_to_call = AVAILABLE_FUNCTIONS[function_name]
            function_result = function_to_call(**function_args)
            self.logger.info(f"结果: {function_result}")
            
            return {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "name": function_name,
                "content": str(function_result)
            }
        else:
            self.logger.error(f"错误: 未找到函数 {function_name}")
            return self._create_error_message(
                tool_call_id, function_name, f"函数 {function_name} 不存在"
            )
    
    def _create_error_message(self, tool_call_id: str, function_name: str, 
                             error: str) -> Dict:
        """创建错误消息"""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": function_name,
            "content": json.dumps({"error": error})
        }
    
    def _print_iteration_header(self, iteration: int):
        """打印迭代头部"""
        self.logger.info("=" * 60)
        self.logger.info(f"[{self.task_name}] 第 {iteration} 轮对话")
        self.logger.info("=" * 60)
    
    def _print_tool_call_info(self, tool_call_id: str, function_name: str, 
                             function_args_str: str):
        """打印工具调用信息"""
        self.logger.info("工具调用:")
        self.logger.info(f"  ID: {tool_call_id}")
        self.logger.info(f"  函数: {function_name}")
        self.logger.info(f"  参数: {function_args_str}")


