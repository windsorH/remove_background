"""启动背景移除服务"""
import sys
import os
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent
src_dir = project_root / "src"

# 添加 src 目录到 Python 路径
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# 设置模型目录
models_dir = project_root / "models"
models_dir.mkdir(exist_ok=True)
os.environ["U2NET_HOME"] = str(models_dir)

# 导入并启动服务
from bg_remover.main import main

if __name__ == "__main__":
    print("="*60)
    print("背景移除服务启动器")
    print("="*60)
    print(f"项目目录: {project_root}")
    print(f"模型目录: {models_dir}")
    print(f"Python路径: {src_dir}")
    print("="*60)
    main()
