"""FastAPI主入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from .api.routes import router
    from .core.config import get_settings
except ImportError:
    from api.routes import router
    from core.config import get_settings


def create_app() -> FastAPI:
    """创建FastAPI应用"""
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
