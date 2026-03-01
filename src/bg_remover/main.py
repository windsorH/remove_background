"""FastAPI主入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging

# 在导入其他模块前先配置路径
import sys
from pathlib import Path
src_dir = Path(__file__).parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

try:
    from bg_remover.api.routes import router
    from bg_remover.core.config import get_settings
    from bg_remover.core.limiter import init_limiter
    from bg_remover.core.thread_pool import init_thread_pool, shutdown_thread_pool
    from bg_remover.core.model_warmer import warm_default_models
except ImportError:
    from api.routes import router
    from core.config import get_settings
    from core.limiter import init_limiter
    from core.thread_pool import init_thread_pool, shutdown_thread_pool
    from core.model_warmer import warm_default_models

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()

    # 启动时初始化
    logger.info("=" * 60)
    logger.info("正在初始化服务...")
    logger.info("=" * 60)

    # 1. 初始化线程池
    logger.info(f"初始化线程池，工作线程数: {settings.thread_pool_workers}")
    init_thread_pool(settings.thread_pool_workers)

    # 2. 初始化并发限制器
    logger.info(f"初始化并发限制器，最大并发: {settings.max_concurrent_requests}")
    init_limiter(settings.max_concurrent_requests)

    # 3. 模型预热
    if settings.enable_model_warmup:
        warmup_models = [m.strip() for m in settings.warmup_models.split(",") if m.strip()]
        logger.info(f"开始预热模型: {warmup_models}")
        try:
            from bg_remover.core.thread_pool import get_thread_pool
            results = await warm_default_models(
                model_path=str(settings.get_model_path()),
                thread_pool=get_thread_pool(),
                models=warmup_models
            )
            success_count = sum(1 for v in results.values() if v)
            logger.info(f"模型预热完成: {success_count}/{len(results)} 成功")
        except Exception as e:
            logger.error(f"模型预热失败: {e}")
    else:
        logger.info("模型预热已禁用")

    logger.info("=" * 60)
    logger.info("服务初始化完成")
    logger.info("=" * 60)

    yield

    # 关闭时清理
    logger.info("正在关闭服务...")
    shutdown_thread_pool(wait=True)
    logger.info("服务已关闭")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()

    app = FastAPI(
        title="Background Remover Service",
        description="HTTP streaming service for image background removal based on rembg",
        version="0.2.0",
        lifespan=lifespan
    )

    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(router)

    return app


app = create_app()


def main():
    """启动服务器"""
    import uvicorn
    import sys
    from pathlib import Path
    
    settings = get_settings()
    
    # 添加 src 目录到 Python 路径
    src_dir = Path(__file__).parent.parent
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    uvicorn.run(
        "bg_remover.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        reload_dirs=[str(src_dir)]
    )


if __name__ == "__main__":
    main()
