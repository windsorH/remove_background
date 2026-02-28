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
