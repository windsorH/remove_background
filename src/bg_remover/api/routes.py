"""API路由"""
import json
import time
import asyncio
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator

from ..models.schemas import (
    RemoveBgUrlRequest,
    RemoveBgResponse,
    HealthResponse,
    StreamEvent
)
from ..services.bg_remover import get_available_models, BackgroundRemover
from ..services.bg_processor import get_processor
from ..services.input_loader import InputLoader
from ..core.config import get_settings
from ..core.limiter import get_limiter
from ..core.model_warmer import get_warmer
from ..core.exceptions import BgRemoverError, TimeoutError as BgTimeoutError

router = APIRouter()


def get_max_file_size_bytes() -> int:
    """获取最大文件大小限制（字节）"""
    settings = get_settings()
    return settings.max_file_size_mb * 1024 * 1024


@router.get("/health")
async def health_check():
    """健康检查 - 包含服务状态详情"""
    settings = get_settings()

    # 获取已预热模型列表
    warmed_models = []
    try:
        warmer = get_warmer()
        warmed_models = warmer.get_warmed_models()
    except RuntimeError:
        pass  # 预热器未初始化

    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.now(),
        "config": {
            "max_concurrent_requests": settings.max_concurrent_requests,
            "request_timeout_seconds": settings.request_timeout_seconds,
            "thread_pool_workers": settings.thread_pool_workers,
            "max_file_size_mb": settings.max_file_size_mb,
            "enable_model_warmup": settings.enable_model_warmup,
        },
        "models": {
            "available": BackgroundRemover.MODELS,
            "warmed": warmed_models,
            "default": settings.default_model
        }
    }


@router.get("/v1/models")
async def list_models():
    """
    获取所有可用的背景移除模型列表
    
    Returns:
        模型列表，包含名称、描述和适用场景
    """
    return {
        "success": True,
        "data": get_available_models()
    }


@router.get("/v1/models/{model_name}/info")
async def get_model_info(model_name: str):
    """
    获取指定模型的详细信息
    
    Args:
        model_name: 模型名称
        
    Returns:
        模型详细信息
    """
    if model_name not in BackgroundRemover.MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"模型 '{model_name}' 不存在。可用模型: {BackgroundRemover.MODELS}"
        )
    
    models_info = get_available_models()
    model_info = next((m for m in models_info if m["name"] == model_name), None)
    
    return {
        "success": True,
        "data": model_info
    }


async def process_stream(
    image_data: bytes,
    output_type: str,
    output_path: str,
    model: str
) -> AsyncGenerator[str, None]:
    """
    流式处理背景移除

    Yields:
        NDJSON格式的流式事件
    """
    start_time = time.time()
    processor = get_processor()

    try:
        # 1. 开始
        yield json.dumps({
            "type": "start",
            "timestamp": int(time.time())
        }) + "\n"

        # 2. 加载/处理
        yield json.dumps({
            "type": "progress",
            "step": "process",
            "percent": 30,
            "message": "正在移除背景..."
        }) + "\n"

        output_data, info = await processor.process_image(
            image_data, model, output_type, output_path
        )

        # 3. 输出
        yield json.dumps({
            "type": "progress",
            "step": "output",
            "percent": 70,
            "message": "正在保存结果..."
        }) + "\n"

        result_url = processor.save_result(output_data, output_type, output_path)

        # 4. 完成
        processing_time = round(time.time() - start_time, 2)
        yield json.dumps({
            "type": "complete",
            "result": {
                "url": result_url,
                "path": output_path,
                "width": info["width"],
                "height": info["height"],
                "format": info["format"],
                "processing_time": processing_time
            }
        }) + "\n"

    except Exception as e:
        yield json.dumps({
            "type": "error",
            "error": str(e)
        }) + "\n"


async def _load_image_from_url(url: str, timeout: int) -> bytes:
    """从URL加载图像（带超时）"""
    loader = InputLoader()
    try:
        return await asyncio.wait_for(
            loader.from_url(url),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="下载图像超时")


async def _remove_bg_url_with_limit(request: RemoveBgUrlRequest):
    """带并发限制的URL背景移除处理"""
    settings = get_settings()
    limiter = get_limiter()
    processor = get_processor()

    async with limiter:
        # 加载图像
        image_data = await _load_image_from_url(
            request.image_url,
            settings.request_timeout_seconds
        )

        if request.stream:
            # 流式响应
            return StreamingResponse(
                process_stream(
                    image_data,
                    request.output_type,
                    request.output_path,
                    request.model
                ),
                media_type="application/x-ndjson"
            )
        else:
            # 非流式响应
            result = await processor.process_and_save(
                image_data,
                request.model,
                request.output_type,
                request.output_path
            )

            return RemoveBgResponse(success=True, data=result)


def _create_error_response(error: Exception, stream: bool = False):
    """创建统一的错误响应"""
    if isinstance(error, BgRemoverError):
        status_code = 400
        error_detail = {
            "success": False,
            "error": error.message,
            "error_code": error.error_code
        }
    elif isinstance(error, HTTPException):
        status_code = error.status_code
        error_detail = {
            "success": False,
            "error": error.detail
        }
    else:
        status_code = 500
        error_detail = {
            "success": False,
            "error": f"服务器内部错误: {str(error)}"
        }

    if stream:
        async def error_stream():
            yield json.dumps({"type": "error", **error_detail}) + "\n"
        return StreamingResponse(error_stream(), media_type="application/x-ndjson")
    else:
        raise HTTPException(status_code=status_code, detail=error_detail["error"])


@router.post("/v1/bg/remove/url")
async def remove_bg_url(request: RemoveBgUrlRequest):
    """
    从URL移除背景

    - stream=true: 返回流式响应（NDJSON）
    - stream=false: 返回普通JSON响应
    """
    try:
        return await _remove_bg_url_with_limit(request)
    except Exception as e:
        return _create_error_response(e, request.stream)


async def _remove_bg_file_with_limit(
    file: UploadFile,
    output_type: str,
    output_path: str,
    model: str,
    stream: bool
):
    """带并发限制的文件背景移除处理"""
    settings = get_settings()
    limiter = get_limiter()
    processor = get_processor()

    async with limiter:
        # 读取上传的文件
        image_data = await file.read()

        # 验证文件大小
        file_size = len(image_data)
        max_file_size_bytes = get_max_file_size_bytes()
        if file_size > max_file_size_bytes:
            max_size_mb = max_file_size_bytes / (1024 * 1024)
            actual_size_mb = file_size / (1024 * 1024)
            error_msg = f"文件大小超过限制。最大允许: {max_size_mb:.1f}MB, 实际: {actual_size_mb:.2f}MB"
            if stream:
                async def error_stream():
                    yield json.dumps({"type": "error", "error": error_msg}) + "\n"
                return StreamingResponse(error_stream(), media_type="application/x-ndjson")
            else:
                raise HTTPException(status_code=413, detail=error_msg)

        if stream:
            # 流式响应
            return StreamingResponse(
                process_stream(image_data, output_type, output_path, model),
                media_type="application/x-ndjson"
            )
        else:
            # 非流式响应
            result = await processor.process_and_save(
                image_data,
                model,
                output_type,
                output_path
            )

            return RemoveBgResponse(success=True, data=result)


@router.post("/v1/bg/remove/file")
async def remove_bg_file(
    file: UploadFile = File(..., description="上传的图像文件"),
    output_type: str = Form(default="file", description="输出类型: file/oss"),
    output_path: str = Form(..., description="输出路径"),
    model: str = Form(default="u2net", description="分割模型"),
    stream: bool = Form(default=False, description="是否流式响应")
):
    """
    从上传文件移除背景

    - stream=true: 返回流式响应（NDJSON）
    - stream=false: 返回普通JSON响应
    """
    try:
        return await _remove_bg_file_with_limit(file, output_type, output_path, model, stream)
    except Exception as e:
        return _create_error_response(e, stream)
