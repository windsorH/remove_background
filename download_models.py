"""下载所有背景移除模型到项目目录"""
import os
import sys
from pathlib import Path

# 模型文件夹路径
MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

# 设置环境变量，让rembg从项目目录加载模型
os.environ["U2NET_HOME"] = str(MODELS_DIR)

# 人物相关模型列表（包括卡通动漫）
MODELS = [
    "u2net",              # 通用模型（默认）
    "u2net_human_seg",    # 人像分割 ⭐
    "isnet-anime",        # 动漫/卡通专用模型 ⭐
    "birefnet-portrait",  # 高精度人像模型 ⭐
]


def download_model(model_name: str) -> bool:
    """
    下载指定模型
    
    Args:
        model_name: 模型名称
        
    Returns:
        bool: 是否下载成功
    """
    print(f"\n{'='*50}", flush=True)
    print(f"正在下载模型: {model_name}", flush=True)
    print(f"{'='*50}", flush=True)
    
    try:
        from rembg import new_session
        
        # 创建session会触发模型下载
        print(f"开始初始化 {model_name} 模型...", flush=True)
        session = new_session(model_name)
        print(f"✅ {model_name} 下载成功!", flush=True)
        return True
        
    except Exception as e:
        print(f"❌ {model_name} 下载失败: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("="*60, flush=True)
    print("背景移除模型下载工具", flush=True)
    print("="*60, flush=True)
    print(f"\n模型将下载到: {MODELS_DIR}", flush=True)
    print(f"总共 {len(MODELS)} 个模型需要下载\n", flush=True)
    
    # 检查rembg是否安装
    try:
        from rembg import new_session
        print("✅ rembg 已安装", flush=True)
    except ImportError:
        print("❌ rembg 未安装，请先安装: pip install rembg", flush=True)
        sys.exit(1)
    
    # 下载所有模型
    success_count = 0
    failed_models = []
    
    for i, model in enumerate(MODELS, 1):
        print(f"\n[{i}/{len(MODELS)}] ", end="", flush=True)
        if download_model(model):
            success_count += 1
        else:
            failed_models.append(model)
    
    # 打印结果
    print("\n" + "="*60, flush=True)
    print("下载完成!", flush=True)
    print("="*60, flush=True)
    print(f"成功: {success_count}/{len(MODELS)}", flush=True)
    
    if failed_models:
        print(f"\n失败的模型: {', '.join(failed_models)}", flush=True)
    
    # 显示模型文件列表
    print(f"\n模型文件夹内容 ({MODELS_DIR}):", flush=True)
    model_files = list(MODELS_DIR.glob("*.onnx"))
    if model_files:
        for f in sorted(model_files):
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  - {f.name} ({size_mb:.1f} MB)", flush=True)
    else:
        print("  (暂无模型文件)", flush=True)
    
    print("\n💡 使用建议:", flush=True)
    print("  - 动漫/卡通人物: 使用 isnet-anime 模型", flush=True)
    print("  - 人像照片: 使用 u2net_human_seg 或 birefnet-portrait", flush=True)
    print("  - 通用场景: 使用 u2net", flush=True)


if __name__ == "__main__":
    main()
