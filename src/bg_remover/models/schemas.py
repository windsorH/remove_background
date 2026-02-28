"""请求和响应模型"""
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class RemoveBgUrlRequest(BaseModel):
    """URL移除背景请求"""
    image_url: str = Field(..., description="图像URL")
    output_type: Literal["file", "oss"] = Field(default="file", description="输出类型")
    output_path: str = Field(..., description="输出路径")
    model: Literal["u2net", "u2net_human_seg", "u2netp", "silueta"] = Field(
        default="u2net", description="分割模型"
    )
    stream: bool = Field(default=False, description="是否流式响应")


class RemoveBgFileRequest(BaseModel):
    """文件移除背景请求（用于非流式）"""
    output_type: Literal["file", "oss"] = Field(default="file", description="输出类型")
    output_path: str = Field(..., description="输出路径")
    model: Literal["u2net", "u2net_human_seg", "u2netp", "silueta"] = Field(
        default="u2net", description="分割模型"
    )
    stream: bool = Field(default=False, description="是否流式响应")


class RemoveBgResponse(BaseModel):
    """移除背景响应"""
    success: bool = Field(..., description="是否成功")
    data: Optional[dict] = Field(default=None, description="响应数据")
    error: Optional[str] = Field(default=None, description="错误信息")


class StreamEvent(BaseModel):
    """流式事件"""
    type: Literal["start", "progress", "complete", "error"] = Field(..., description="事件类型")
    timestamp: Optional[int] = Field(default=None, description="时间戳")
    step: Optional[str] = Field(default=None, description="当前步骤")
    percent: Optional[int] = Field(default=None, description="进度百分比")
    message: Optional[str] = Field(default=None, description="进度消息")
    result: Optional[dict] = Field(default=None, description="结果数据")
    error: Optional[str] = Field(default=None, description="错误信息")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(default="ok", description="服务状态")
    version: str = Field(default="0.1.0", description="版本号")
    timestamp: datetime = Field(default_factory=datetime.now, description="当前时间")
