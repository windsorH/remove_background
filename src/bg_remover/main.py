"""FastAPI主入口"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import asyncio

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
except ImportError:
    from api.routes import router
    from core.config import get_settings
    from core.limiter import init_limiter


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    settings = get_settings()

    # 初始化并发限制器
    init_limiter(settings.max_concurrent_requests)

    app = FastAPI(
        title="Background Remover Service",
        description="HTTP streaming service for image background removal based on rembg",
        version="0.1.0"
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
