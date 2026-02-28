"""线程池管理器"""
from concurrent.futures import ThreadPoolExecutor
from typing import Optional


class ThreadPoolManager:
    """全局线程池管理器"""

    _instance: Optional['ThreadPoolManager'] = None
    _executor: Optional[ThreadPoolExecutor] = None

    def __new__(cls, max_workers: int = 4):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_workers: int = 4):
        if self._initialized:
            return

        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="bg_remover_"
        )
        self._initialized = True

    @property
    def executor(self) -> ThreadPoolExecutor:
        """获取线程池执行器"""
        if self._executor is None:
            raise RuntimeError("线程池未初始化")
        return self._executor

    def shutdown(self, wait: bool = True):
        """关闭线程池"""
        if self._executor is not None:
            self._executor.shutdown(wait=wait)
            self._executor = None

    @classmethod
    def get_instance(cls) -> 'ThreadPoolManager':
        """获取线程池管理器实例"""
        if cls._instance is None:
            raise RuntimeError("线程池管理器未初始化，请先调用 init_thread_pool()")
        return cls._instance


def init_thread_pool(max_workers: int = 4) -> ThreadPoolManager:
    """
    初始化全局线程池

    Args:
        max_workers: 最大工作线程数，默认为4

    Returns:
        ThreadPoolManager: 线程池管理器实例
    """
    return ThreadPoolManager(max_workers)


def get_thread_pool() -> ThreadPoolExecutor:
    """
    获取线程池执行器

    Returns:
        ThreadPoolExecutor: 线程池执行器
    """
    return ThreadPoolManager.get_instance().executor


def shutdown_thread_pool(wait: bool = True):
    """关闭线程池"""
    ThreadPoolManager.get_instance().shutdown(wait=wait)
