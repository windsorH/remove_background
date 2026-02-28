"""输入加载器"""
import httpx
from pathlib import Path
from typing import Union


class InputLoader:
    """图像输入加载器"""
    
    async def from_url(self, url: str, timeout: int = 30) -> bytes:
        """
        从URL加载图像
        
        Args:
            url: 图像URL
            timeout: 超时时间（秒）
            
        Returns:
            图像字节数据
            
        Raises:
            httpx.HTTPError: 下载失败
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=timeout, follow_redirects=True)
            response.raise_for_status()
            return response.content
    
    def from_file(self, path: Union[str, Path]) -> bytes:
        """
        从本地文件加载图像
        
        Args:
            path: 文件路径
            
        Returns:
            图像字节数据
            
        Raises:
            FileNotFoundError: 文件不存在
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")
        return path.read_bytes()
    
    async def load(self, source: Union[str, bytes, Path]) -> bytes:
        """
        通用加载方法
        
        Args:
            source: URL字符串、字节数据或文件路径
            
        Returns:
            图像字节数据
        """
        if isinstance(source, bytes):
            return source
        
        if isinstance(source, Path):
            return self.from_file(source)
        
        source_str = str(source)
        if source_str.startswith(("http://", "https://")):
            return await self.from_url(source_str)
        else:
            return self.from_file(source_str)
