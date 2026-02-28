"""并发限制器"""
import asyncio
from functools import wraps
from typing import Callable, Any


class ConcurrencyLimiter:
    """并发请求限制器"""

    def __init__(self, max_concurrent: int = 5):
        """
        初始化并发限制器

        Args:
            max_concurrent: 最大并发请求数
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent

    async def acquire(self):
        """获取信号量"""
        await self.semaphore.acquire()

    def release(self):
        """释放信号量"""
        self.semaphore.release()

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()


def with_concurrency_limit(limiter: ConcurrencyLimiter):
    """
    装饰器：限制函数并发执行数

    Args:
        limiter: 并发限制器实例
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            async with limiter:
                return await func(*args, **kwargs)
        return wrapper
    return decorator


# 全局限制器实例（将在应用启动时初始化）
_global_limiter: ConcurrencyLimiter | None = None


def init_limiter(max_concurrent: int = 5) -> ConcurrencyLimiter:
    """
    初始化全局并发限制器

    Args:
        max_concurrent: 最大并发请求数

    Returns:
        ConcurrencyLimiter: 并发限制器实例
    """
    global _global_limiter
    _global_limiter = ConcurrencyLimiter(max_concurrent)
    return _global_limiter


def get_limiter() -> ConcurrencyLimiter:
    """
    获取全局并发限制器

    Returns:
        ConcurrencyLimiter: 并发限制器实例

    Raises:
        RuntimeError: 如果限制器未初始化
    """
    if _global_limiter is None:
        raise RuntimeError("并发限制器未初始化，请先调用 init_limiter()")
    return _global_limiter
