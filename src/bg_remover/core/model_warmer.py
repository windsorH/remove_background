"""模型预热器"""
import asyncio
import logging
from typing import List, Optional
from concurrent.futures import wait as futures_wait

logger = logging.getLogger(__name__)


class ModelWarmer:
    """模型预热器 - 在应用启动时预加载常用模型"""

    def __init__(self, model_path: Optional[str] = None):
        """
        初始化模型预热器

        Args:
            model_path: 模型文件夹路径
        """
        self.model_path = model_path
        self.warmed_models: set[str] = set()

    async def warm_model(
        self,
        model_name: str,
        thread_pool=None
    ) -> bool:
        """
        预热单个模型

        Args:
            model_name: 模型名称
            thread_pool: 可选的线程池，用于异步加载

        Returns:
            bool: 是否成功预热
        """
        try:
            logger.info(f"开始预热模型: {model_name}")

            # 导入在这里避免循环依赖
            from ..services.bg_remover import get_remover

            if thread_pool:
                # 在线程池中执行模型加载
                loop = asyncio.get_event_loop()
                remover = await loop.run_in_executor(
                    thread_pool,
                    get_remover,
                    model_name,
                    self.model_path
                )
            else:
                remover = get_remover(model_name, self.model_path)

            # 访问session属性触发模型加载
            _ = remover.session

            self.warmed_models.add(model_name)
            logger.info(f"模型预热成功: {model_name}")
            return True

        except Exception as e:
            logger.error(f"模型预热失败 {model_name}: {e}")
            return False

    async def warm_models(
        self,
        model_names: List[str],
        thread_pool=None,
        concurrent: bool = True
    ) -> dict[str, bool]:
        """
        预热多个模型

        Args:
            model_names: 模型名称列表
            thread_pool: 可选的线程池
            concurrent: 是否并发预热，默认为True

        Returns:
            dict[str, bool]: 每个模型的预热结果
        """
        results = {}

        if concurrent:
            # 并发预热所有模型
            tasks = [
                self.warm_model(name, thread_pool)
                for name in model_names
            ]
            completed = await asyncio.gather(*tasks, return_exceptions=True)

            for name, result in zip(model_names, completed):
                if isinstance(result, Exception):
                    logger.error(f"模型预热异常 {name}: {result}")
                    results[name] = False
                else:
                    results[name] = result
        else:
            # 顺序预热
            for name in model_names:
                results[name] = await self.warm_model(name, thread_pool)

        return results

    def get_warmed_models(self) -> List[str]:
        """获取已预热的模型列表"""
        return list(self.warmed_models)

    def is_warmed(self, model_name: str) -> bool:
        """检查模型是否已预热"""
        return model_name in self.warmed_models


# 全局预热器实例
_warmer_instance: Optional[ModelWarmer] = None


def init_warmer(model_path: Optional[str] = None) -> ModelWarmer:
    """
    初始化全局模型预热器

    Args:
        model_path: 模型文件夹路径

    Returns:
        ModelWarmer: 模型预热器实例
    """
    global _warmer_instance
    _warmer_instance = ModelWarmer(model_path)
    return _warmer_instance


def get_warmer() -> ModelWarmer:
    """
    获取全局模型预热器

    Returns:
        ModelWarmer: 模型预热器实例

    Raises:
        RuntimeError: 如果预热器未初始化
    """
    if _warmer_instance is None:
        raise RuntimeError("模型预热器未初始化，请先调用 init_warmer()")
    return _warmer_instance


async def warm_default_models(
    model_path: Optional[str] = None,
    thread_pool=None,
    models: Optional[List[str]] = None
) -> dict[str, bool]:
    """
    预热默认模型集合

    Args:
        model_path: 模型文件夹路径
        thread_pool: 可选的线程池
        models: 要预热的模型列表，默认预热常用模型

    Returns:
        dict[str, bool]: 预热结果
    """
    if models is None:
        # 默认预热最常用的模型
        models = ["u2net", "u2net_human_seg"]

    warmer = init_warmer(model_path)
    return await warmer.warm_models(models, thread_pool, concurrent=True)
