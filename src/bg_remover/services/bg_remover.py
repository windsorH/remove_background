"""背景移除核心服务"""
from rembg import remove, new_session
from PIL import Image
import io
import os
from typing import Optional
from functools import lru_cache


class BackgroundRemover:
    """背景移除器"""
    
    MODELS = [
        "u2net",              # 通用模型（默认）
        "u2net_human_seg",    # 人像分割 ⭐
        "isnet-anime",        # 动漫/卡通专用模型 ⭐
        "birefnet-portrait",  # 高精度人像模型 ⭐
    ]
    
    def __init__(self, model_name: str = "u2net", model_path: Optional[str] = None):
        """
        初始化背景移除器
        
        Args:
            model_name: 模型名称，可选 u2net, u2net_human_seg, u2netp, silueta, 
                       isnet-anime(动漫推荐), isnet-general-use, birefnet-general等
            model_path: 自定义模型文件夹路径，默认使用系统缓存目录
        """
        if model_name not in self.MODELS:
            raise ValueError(f"不支持的模型: {model_name}，可选: {self.MODELS}")
        
        self.model_name = model_name
        self.model_path = model_path
        self._session = None
        
        # 如果指定了模型路径，设置环境变量
        if model_path:
            os.environ["U2NET_HOME"] = model_path
    
    @property
    def session(self):
        """懒加载session"""
        if self._session is None:
            self._session = new_session(self.model_name)
        return self._session
    
    def remove(self, image_data: bytes) -> bytes:
        """
        移除图像背景
        
        Args:
            image_data: 输入图像字节数据
            
        Returns:
            PNG格式的RGBA图像字节数据
        """
        input_image = Image.open(io.BytesIO(image_data))
        
        output_image = remove(input_image, session=self.session)
        
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")
        return output_buffer.getvalue()
    
    def remove_with_info(self, image_data: bytes) -> tuple[bytes, dict]:
        """
        移除背景并返回图像信息
        
        Args:
            image_data: 输入图像字节数据
            
        Returns:
            (输出图像字节, 图像信息字典)
        """
        input_image = Image.open(io.BytesIO(image_data))
        input_size = input_image.size
        
        output_image = remove(input_image, session=self.session)
        
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format="PNG")
        output_data = output_buffer.getvalue()
        
        info = {
            "width": output_image.width,
            "height": output_image.height,
            "format": "PNG",
            "mode": "RGBA",
            "input_width": input_size[0],
            "input_height": input_size[1],
            "output_size_bytes": len(output_data)
        }
        
        return output_data, info


def _get_model_path_from_config() -> Optional[str]:
    """从配置获取模型路径"""
    try:
        from ..core.config import get_settings
        settings = get_settings()
        return str(settings.get_model_path())
    except Exception:
        return None


@lru_cache(maxsize=8)
def _create_remover(model_name: str, model_path: str) -> BackgroundRemover:
    """
    创建背景移除器实例（带LRU缓存）
    
    Args:
        model_name: 模型名称
        model_path: 模型文件夹路径
        
    Returns:
        BackgroundRemover: 背景移除器实例
    """
    return BackgroundRemover(model_name, model_path if model_path else None)


def get_remover(model_name: str = "u2net", model_path: Optional[str] = None) -> BackgroundRemover:
    """
    获取或创建移除器实例（带LRU缓存，最多缓存8个实例）
    
    Args:
        model_name: 模型名称
        model_path: 自定义模型文件夹路径，默认从配置读取
        
    Returns:
        BackgroundRemover: 背景移除器实例
    """
    # 如果没有指定模型路径，从配置读取
    if model_path is None:
        model_path = _get_model_path_from_config() or ""
    
    return _create_remover(model_name, model_path)


def get_available_models() -> list[dict]:
    """
    获取所有可用模型的详细信息
    
    Returns:
        list[dict]: 模型信息列表
    """
    return [
        {"name": "u2net", "description": "通用模型（默认）", "use_case": "通用场景"},
        {"name": "u2net_human_seg", "description": "人像分割模型⭐", "use_case": "人像照片"},
        {"name": "isnet-anime", "description": "动漫专用模型⭐", "use_case": "动漫/卡通人物"},
        {"name": "birefnet-portrait", "description": "高精度人像模型⭐", "use_case": "高质量人像分割"},
    ]
