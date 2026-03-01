"""OSS上传器"""
import oss2
from pathlib import Path
from typing import Optional, Union

from ..core.config import get_settings


class OSSUploader:
    """阿里云OSS上传器"""
    
    def __init__(
        self,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
        bucket: Optional[str] = None,
        endpoint: Optional[str] = None
    ):
        """
        初始化OSS上传器
        
        Args:
            access_key_id: AccessKey ID
            access_key_secret: AccessKey Secret
            bucket: Bucket名称
            endpoint: Endpoint地址
        """
        settings = get_settings()
        
        self.access_key_id = access_key_id or settings.oss_access_key_id
        self.access_key_secret = access_key_secret or settings.oss_access_key_secret
        self.bucket_name = bucket or settings.oss_bucket
        self.endpoint = endpoint or settings.oss_endpoint
        
        self._bucket = None
    
    @property
    def bucket(self):
        """懒加载bucket"""
        if self._bucket is None:
            if not all([self.access_key_id, self.access_key_secret, self.bucket_name]):
                raise ValueError("OSS配置不完整，请检查access_key_id, access_key_secret, bucket")
            
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self._bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)
        return self._bucket
    
    def upload(self, key: str, data: bytes) -> str:
        """
        上传数据到OSS
        
        Args:
            key: OSS对象键（路径）
            data: 要上传的字节数据
            
        Returns:
            访问URL
        """
        self.bucket.put_object(key, data)
        return f"https://{self.bucket_name}.{self.endpoint}/{key}"
    
    def upload_file(self, key: str, file_path: Union[str, Path]) -> str:
        """
        上传文件到OSS
        
        Args:
            key: OSS对象键（路径）
            file_path: 本地文件路径
            
        Returns:
            访问URL
        """
        file_path = Path(file_path)
        self.bucket.put_object_from_file(key, str(file_path))
        return f"https://{self.bucket_name}.{self.endpoint}/{key}"
    
    def generate_signed_url(self, key: str, expires: int = 3600) -> str:
        """
        生成带签名的临时访问URL
        
        Args:
            key: OSS对象键
            expires: 过期时间（秒）
            
        Returns:
            签名URL
        """
        return self.bucket.sign_url('GET', key, expires)
    
    def is_configured(self) -> bool:
        """检查OSS是否已配置"""
        return all([self.access_key_id, self.access_key_secret, self.bucket_name])


# 全局上传器实例
_uploader_instance: Optional[OSSUploader] = None


def get_uploader() -> OSSUploader:
    """获取OSS上传器单例"""
    global _uploader_instance
    if _uploader_instance is None:
        _uploader_instance = OSSUploader()
    return _uploader_instance
