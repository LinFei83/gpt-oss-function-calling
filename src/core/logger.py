"""
通用日志模块
提供统一的日志记录功能，支持控制台和文件输出
"""
import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（仅用于控制台）"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def format(self, record):
        """格式化日志记录，添加颜色"""
        # 保存原始levelname
        levelname = record.levelname
        
        # 添加颜色
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # 格式化消息
        result = super().format(record)
        
        # 恢复原始levelname
        record.levelname = levelname
        
        return result


class Logger:
    """日志管理器类"""
    
    _instances = {}  # 存储不同名称的logger实例
    
    def __init__(self, name: str = "app", 
                 level: int = logging.INFO,
                 log_file: Optional[str] = None,
                 enable_console: bool = True,
                 enable_color: bool = True):
        """
        初始化日志器
        
        参数:
            name: 日志器名称
            level: 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
            log_file: 日志文件路径，如果为None则不写入文件
            enable_console: 是否启用控制台输出
            enable_color: 是否启用彩色输出（仅控制台）
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加handler
        if self.logger.handlers:
            return
        
        # 日志格式
        console_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        file_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # 添加控制台处理器
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            if enable_color:
                console_formatter = ColoredFormatter(console_format, date_format)
            else:
                console_formatter = logging.Formatter(console_format, date_format)
            
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # 添加文件处理器
        if log_file:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(file_format, date_format)
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录一般信息"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告信息"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误信息"""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """记录异常信息（包含堆栈跟踪）"""
        self.logger.exception(message, *args, **kwargs)
    
    def set_level(self, level: int):
        """动态设置日志级别"""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)
    
    @classmethod
    def get_logger(cls, name: str = "app", **kwargs) -> 'Logger':
        """
        获取日志器实例（单例模式）
        
        参数:
            name: 日志器名称
            **kwargs: 其他初始化参数
        
        返回:
            Logger实例
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name, **kwargs)
        return cls._instances[name]


# 创建默认日志器实例
def setup_default_logger(level: int = logging.INFO, 
                         log_file: Optional[str] = None,
                         enable_color: bool = True) -> Logger:
    """
    设置默认日志器
    
    参数:
        level: 日志级别
        log_file: 日志文件路径
        enable_color: 是否启用彩色输出
    
    返回:
        Logger实例
    """
    return Logger.get_logger(
        name="app",
        level=level,
        log_file=log_file,
        enable_console=True,
        enable_color=enable_color
    )


# 便捷的全局日志函数
_default_logger = None

def get_default_logger() -> Logger:
    """获取默认日志器"""
    global _default_logger
    if _default_logger is None:
        _default_logger = setup_default_logger()
    return _default_logger


def debug(message: str, *args, **kwargs):
    """全局调试日志"""
    get_default_logger().debug(message, *args, **kwargs)


def info(message: str, *args, **kwargs):
    """全局信息日志"""
    get_default_logger().info(message, *args, **kwargs)


def warning(message: str, *args, **kwargs):
    """全局警告日志"""
    get_default_logger().warning(message, *args, **kwargs)


def error(message: str, *args, **kwargs):
    """全局错误日志"""
    get_default_logger().error(message, *args, **kwargs)


def critical(message: str, *args, **kwargs):
    """全局严重错误日志"""
    get_default_logger().critical(message, *args, **kwargs)


def exception(message: str, *args, **kwargs):
    """全局异常日志"""
    get_default_logger().exception(message, *args, **kwargs)


# 日志级别常量（方便导入使用）
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


if __name__ == "__main__":
    # 测试代码
    print("测试日志模块...")
    
    # 设置默认日志器
    logger = setup_default_logger(level=DEBUG, log_file="logs/app.log")
    
    # 测试各种日志级别
    logger.debug("这是一条调试信息")
    logger.info("这是一条普通信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    logger.critical("这是一条严重错误信息")
    
    # 测试全局函数
    info("使用全局函数记录信息")
    warning("使用全局函数记录警告")
    
    print("\n日志已记录到控制台和文件（如果配置了文件）")

