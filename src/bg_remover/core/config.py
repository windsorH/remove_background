"""配置管理"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    # OSS配置
    oss_access_key_id: str = ""
    oss_access_key_secret: str = ""
    oss_bucket: str = ""
    oss_endpoint: str = "oss-cn-beijing.aliyuncs.com"
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    
    # 输出配置
    output_dir: str = "./output"
    
    # 模型配置
    model_dir: str = "./models"  # 模型文件夹路径
    default_model: str = "u2net"  # 默认模型

    # 上传限制配置
    max_file_size_mb: int = 10  # 最大文件大小（MB）
    max_request_size_mb: int = 50  # 最大请求体大小（MB）

    # 并发控制配置
    max_concurrent_requests: int = 5  # 最大并发请求数
    request_timeout_seconds: int = 120  # 请求超时时间（秒）

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def get_model_path(self) -> Path:
        """获取模型文件夹绝对路径"""
        return Path(self.model_dir).resolve()


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
