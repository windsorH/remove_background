"""背景移除处理服务"""
import asyncio
import time
from typing import Optional, Tuple
from fastapi import HTTPException

from .bg_remover import get_remover, BackgroundRemover
from .output_saver import OutputSaver
from .oss_uploader import get_uploader
from ..core.config import get_settings


class BgProcessor:
    """背景移除处理器 - 封装核心处理逻辑"""

    def __init__(self):
        self.settings = get_settings()

    async def process_image(
        self,
        image_data: bytes,
        model: str,
        output_type: str,
        output_path: str
    ) -> Tuple[bytes, dict]:
        """
        处理图像移除背景

        Args:
            image_data: 输入图像字节数据
            model: 模型名称
            output_type: 输出类型 (file/oss)
            output_path: 输出路径

        Returns:
            (输出数据, 处理信息)
        """
        remover = get_remover(model)

        try:
            output_data, info = await asyncio.wait_for(
                asyncio.to_thread(remover.remove_with_info, image_data),
                timeout=self.settings.request_timeout_seconds
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="处理图像超时")

        return output_data, info

    def save_result(
        self,
        output_data: bytes,
        output_type: str,
        output_path: str
    ) -> str:
        """
        保存处理结果

        Args:
            output_data: 输出图像字节数据
            output_type: 输出类型 (file/oss)
            output_path: 输出路径

        Returns:
            结果URL或路径
        """
        if output_type == "oss":
            uploader = get_uploader()
            if not uploader.is_configured():
                raise HTTPException(status_code=500, detail="OSS未配置")
            return uploader.upload(output_path, output_data)
        else:
            saver = OutputSaver(self.settings.output_dir)
            return saver.save(output_data, output_path)

    async def process_and_save(
        self,
        image_data: bytes,
        model: str,
        output_type: str,
        output_path: str
    ) -> dict:
        """
        处理图像并保存结果（完整流程）

        Args:
            image_data: 输入图像字节数据
            model: 模型名称
            output_type: 输出类型 (file/oss)
            output_path: 输出路径

        Returns:
            处理结果字典
        """
        start_time = time.time()

        # 处理图像
        output_data, info = await self.process_image(
            image_data, model, output_type, output_path
        )

        # 保存结果
        result_url = self.save_result(output_data, output_type, output_path)

        processing_time = round(time.time() - start_time, 2)

        return {
            "url": result_url,
            "path": output_path,
            "width": info["width"],
            "height": info["height"],
            "format": info["format"],
            "processing_time": processing_time
        }


# 全局处理器实例
_processor_instance: Optional[BgProcessor] = None


def get_processor() -> BgProcessor:
    """获取背景移除处理器单例"""
    global _processor_instance
    if _processor_instance is None:
        _processor_instance = BgProcessor()
    return _processor_instance
