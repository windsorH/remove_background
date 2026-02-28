"""输出保存器"""
from pathlib import Path
from typing import Union


class OutputSaver:
    """图像输出保存器"""
    
    def __init__(self, base_dir: Union[str, Path] = "./output"):
        """
        初始化保存器
        
        Args:
            base_dir: 基础输出目录
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, data: bytes, path: Union[str, Path]) -> str:
        """
        保存数据到文件
        
        Args:
            data: 要保存的字节数据
            path: 相对路径或绝对路径
            
        Returns:
            保存的绝对路径
        """
        output_path = Path(path)
        
        # 如果是相对路径，基于base_dir
        if not output_path.is_absolute():
            output_path = self.base_dir / output_path
        
        # 创建父目录
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        output_path.write_bytes(data)
        
        return str(output_path.absolute())
    
    def get_full_path(self, path: Union[str, Path]) -> Path:
        """
        获取完整路径
        
        Args:
            path: 相对路径或绝对路径
            
        Returns:
            完整路径
        """
        output_path = Path(path)
        if not output_path.is_absolute():
            output_path = self.base_dir / output_path
        return output_path
