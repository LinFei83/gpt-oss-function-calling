"""
子任务执行器模块
负责管理和执行从主模型委派的子任务
支持预定义的专门代理（Agent）
"""
import json
import yaml
import os
from typing import Dict, List, Optional, Any
from src.core.logger import Logger


class SubTaskExecutor:
    """
    子任务执行器
    
    主要功能：
    1. 加载和管理预定义的专门代理配置
    2. 接收主模型的子任务请求
    3. 根据代理类型创建独立的子模型实例执行任务
    4. 将执行结果返回给主模型
    5. 保持子任务的上下文独立，不影响主任务
    """
    
    def __init__(self, api_url: str = "http://192.168.0.19:8974/v1/chat/completions",
                 model: str = "gpt-oss-120b",
                 agents_config_path: str = "config/agents.yaml",
                 api_key: str = "sk-145253"):
        """
        初始化子任务执行器
        
        参数:
            api_url: API 服务器地址
            model: 模型名称
            agents_config_path: 代理配置文件路径
            api_key: API 密钥
        """
        self.api_url = api_url
        self.model = model
        self.api_key = api_key
        self.logger = Logger.get_logger("SubTaskExecutor")
        
        # 加载代理配置
        self.agents_config = self._load_agents_config(agents_config_path)
        self.logger.info(f"已加载 {len(self.agents_config)} 个代理配置")
    
    def _load_agents_config(self, config_path: str) -> Dict[str, Dict]:
        """
        加载代理配置文件
        
        参数:
            config_path: 配置文件路径
        
        返回:
            代理配置字典
        """
        if not os.path.exists(config_path):
            self.logger.warning(f"代理配置文件不存在: {config_path}，使用空配置")
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not isinstance(config, dict):
                self.logger.error("代理配置格式错误")
                return {}
            
            return config
        except Exception as e:
            self.logger.error(f"加载代理配置失败: {e}")
            return {}
    
    def get_available_agents(self) -> List[str]:
        """
        获取所有可用的代理类型
        
        返回:
            代理类型列表
        """
        return list(self.agents_config.keys())
    
    def get_agent_info(self, agent_type: str) -> Optional[Dict]:
        """
        获取指定代理的信息
        
        参数:
            agent_type: 代理类型
        
        返回:
            代理信息字典，如果不存在返回 None
        """
        return self.agents_config.get(agent_type)
    
    def execute(self, agent_type: str, task_description: str) -> Dict[str, Any]:
        """
        执行子任务（使用指定的代理类型）
        
        参数:
            agent_type: 代理类型（如 "math_agent", "home_control_agent"）
            task_description: 子任务的描述
        
        返回:
            包含执行结果的字典
        """
        from src.core.chat_client import ChatClient
        from src.tools import get_tools_for_groups
        
        # 检查代理类型是否存在
        if agent_type not in self.agents_config:
            error_msg = f"未知的代理类型: {agent_type}。可用的代理: {', '.join(self.get_available_agents())}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "agent_type": agent_type,
                "task_description": task_description
            }
        
        # 获取代理配置
        agent_config = self.agents_config[agent_type]
        agent_name = agent_config.get("name", agent_type)
        tool_groups = agent_config.get("tool_groups", [])
        identity = agent_config.get("identity", "")
        reasoning_effort = agent_config.get("reasoning_effort", "low")
        max_iterations = agent_config.get("max_iterations", 10)
        
        self.logger.info("=" * 80)
        self.logger.info(f"[子代理启动] {agent_name}")
        self.logger.info(f"代理类型: {agent_type}")
        self.logger.info(f"任务描述: {task_description}")
        self.logger.info(f"可用工具分组: {tool_groups}")
        self.logger.info("=" * 80)
        
        # 获取代理可用的工具
        tools = get_tools_for_groups(tool_groups)
        
        # 构建子任务的消息
        messages = [
            {
                "role": "user",
                "content": task_description
            }
        ]
        
        # 创建子任务的 ChatClient 实例（传入代理名称用于日志标识）
        client = ChatClient(
            api_url=self.api_url, 
            model=self.model,
            task_name=agent_name,  # 使用代理名称作为任务标识
            api_key=self.api_key  # 传递 API key
        )
        
        try:
            # 执行子任务
            result = client.chat(
                messages=messages,
                tools=tools,
                max_iterations=max_iterations,
                reasoning_effort=reasoning_effort,
                model_identity=identity,
                temperature=0.3,  # 较低的温度，更确定性的输出
                max_tokens=1500,  # 限制输出长度
                stream=False  # 子任务不使用流式输出
            )
            
            self.logger.info("=" * 80)
            self.logger.info(f"[子代理完成] {agent_name}")
            self.logger.info(f"执行结果: {result}")
            self.logger.info("=" * 80)
            
            return {
                "success": True,
                "result": result,
                "agent_type": agent_type,
                "agent_name": agent_name,
                "task_description": task_description
            }
            
        except Exception as e:
            self.logger.error(f"子代理执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_type": agent_type,
                "agent_name": agent_name,
                "task_description": task_description
            }


# 全局子任务执行器实例（单例模式）
_subtask_executor_instance = None


def get_subtask_executor(api_key: str = "sk-145253") -> SubTaskExecutor:
    """
    获取子任务执行器的全局实例（单例模式）
    
    参数:
        api_key: API 密钥
    
    返回:
        SubTaskExecutor 实例
    """
    global _subtask_executor_instance
    if _subtask_executor_instance is None:
        _subtask_executor_instance = SubTaskExecutor(api_key=api_key)
    return _subtask_executor_instance

