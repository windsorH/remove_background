"""自定义异常类"""


class BgRemoverError(Exception):
    """基础异常类"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ImageLoadError(BgRemoverError):
    """图像加载错误"""
    
    def __init__(self, message: str = "图像加载失败"):
        super().__init__(message, error_code="IMAGE_LOAD_ERROR")


class ImageProcessError(BgRemoverError):
    """图像处理错误"""
    
    def __init__(self, message: str = "图像处理失败"):
        super().__init__(message, error_code="IMAGE_PROCESS_ERROR")


class ModelNotFoundError(BgRemoverError):
    """模型未找到错误"""
    
    def __init__(self, model_name: str):
        super().__init__(
            f"模型 '{model_name}' 不存在",
            error_code="MODEL_NOT_FOUND"
        )


class OSSConfigError(BgRemoverError):
    """OSS配置错误"""
    
    def __init__(self, message: str = "OSS未配置"):
        super().__init__(message, error_code="OSS_CONFIG_ERROR")


class FileSizeError(BgRemoverError):
    """文件大小错误"""
    
    def __init__(self, max_size_mb: float, actual_size_mb: float):
        super().__init__(
            f"文件大小超过限制。最大允许: {max_size_mb:.1f}MB, 实际: {actual_size_mb:.2f}MB",
            error_code="FILE_SIZE_EXCEEDED"
        )


class TimeoutError(BgRemoverError):
    """超时错误"""
    
    def __init__(self, operation: str = "操作"):
        super().__init__(
            f"{operation}超时",
            error_code="TIMEOUT"
        )
