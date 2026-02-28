"""文件进文件出 - 批量处理示例"""
import httpx
import asyncio
import os
from pathlib import Path
from typing import List, Tuple
import time

BASE_URL = "http://localhost:8000"

# 测试配置
INPUT_DIR = "D:/workspace/remove_background/data"  # 输入文件夹
OUTPUT_DIR = "D:/workspace/remove_background/output"  # 输出文件夹
MODEL = "isnet-anime"  # 模型选择
CONCURRENT_LIMIT = 3  # 并发数限制


async def remove_bg_file_single(
    client: httpx.AsyncClient,
    input_path: str,
    output_path: str,
    model: str = "u2net"
) -> Tuple[bool, str, dict]:
    """
    单文件背景移除
    
    Returns:
        (成功状态, 输入文件, 结果信息)
    """
    try:
        with open(input_path, "rb") as f:
            files = {"file": (Path(input_path).name, f, "image/png")}
            data = {
                "output_type": "file",
                "output_path": output_path,
                "model": model,
                "stream": "false"
            }
            
            response = await client.post(
                f"{BASE_URL}/v1/bg/remove/file",
                files=files,
                data=data,
                timeout=120.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return True, input_path, result["data"]
                else:
                    return False, input_path, {"error": result}
            else:
                return False, input_path, {"error": f"HTTP {response.status_code}"}
                
    except Exception as e:
        return False, input_path, {"error": str(e)}


async def process_batch_with_semaphore(
    client: httpx.AsyncClient,
    tasks: List[Tuple[str, str, str]],
    max_concurrent: int = 3
) -> List[Tuple[bool, str, dict]]:
    """
    使用信号量控制并发数批量处理
    
    Args:
        client: HTTP客户端
        tasks: 任务列表 [(input_path, output_path, model), ...]
        max_concurrent: 最大并发数
    
    Returns:
        结果列表
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_limit(input_path: str, output_path: str, model: str):
        async with semaphore:
            result = await remove_bg_file_single(client, input_path, output_path, model)
            # 打印进度
            status = "✅" if result[0] else "❌"
            print(f"   {status} {Path(input_path).name}")
            return result
    
    # 创建所有任务
    coroutines = [
        process_with_limit(input_path, output_path, model)
        for input_path, output_path, model in tasks
    ]
    
    # 并发执行
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    
    # 处理异常结果
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            input_path = tasks[i][0]
            processed_results.append((False, input_path, {"error": str(result)}))
        else:
            processed_results.append(result)
    
    return processed_results


async def batch_process_files(
    input_dir: str,
    output_dir: str,
    model: str = "u2net",
    pattern: str = "*.png"
):
    """
    批量处理文件夹中的图像
    
    Args:
        input_dir: 输入文件夹
        output_dir: 输出文件夹
        model: 使用的模型
        pattern: 文件匹配模式
    """
    print(f"\n{'='*60}")
    print(f"批量文件处理")
    print(f"{'='*60}")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"使用模型: {model}")
    print(f"并发限制: {CONCURRENT_LIMIT}")
    
    # 检查输入目录
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 错误: 输入目录不存在: {input_dir}")
        return
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 获取所有图像文件
    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp", "*.tiff", "*.tif", "*.gif"]:
        image_files.extend(input_path.glob(ext))

    if not image_files:
        print(f"❌ 错误: 未找到图像文件")
        return

    print(f"\n找到 {len(image_files)} 个图像文件")
    print(f"开始处理...\n")
    
    # 准备任务列表
    tasks = []
    for img_file in image_files:
        output_file = output_path / f"{img_file.stem}_nobg.png"
        tasks.append((str(img_file), str(output_file), model))
    
    # 批量处理
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        results = await process_batch_with_semaphore(
            client, tasks, CONCURRENT_LIMIT
        )
    
    end_time = time.time()
    
    # 统计结果
    success_count = sum(1 for r in results if r[0])
    failed_count = len(results) - success_count
    total_time = round(end_time - start_time, 2)
    
    print(f"\n{'='*60}")
    print(f"批量处理完成")
    print(f"{'='*60}")
    print(f"总文件数: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"总耗时: {total_time}s")
    print(f"平均每个: {round(total_time/len(results), 2)}s")
    
    # 显示失败的文件
    failed_files = [r[1] for r in results if not r[0]]
    if failed_files:
        print(f"\n失败的文件:")
        for f in failed_files:
            print(f"   - {Path(f).name}")


async def batch_process_with_progress(
    input_dir: str,
    output_dir: str,
    model: str = "u2net"
):
    """
    批量处理带进度显示（顺序处理）
    """
    print(f"\n{'='*60}")
    print(f"批量文件处理 - 顺序模式")
    print(f"{'='*60}")
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"使用模型: {model}")
    
    # 检查输入目录
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 错误: 输入目录不存在: {input_dir}")
        return
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 获取所有图像文件
    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp", "*.tiff", "*.tif", "*.gif"]:
        image_files.extend(input_path.glob(ext))

    if not image_files:
        print(f"❌ 错误: 未找到图像文件")
        return

    print(f"\n找到 {len(image_files)} 个图像文件")
    
    # 顺序处理
    start_time = time.time()
    success_count = 0
    failed_files = []
    
    async with httpx.AsyncClient() as client:
        for i, img_file in enumerate(image_files, 1):
            output_file = output_path / f"{img_file.stem}_nobg.png"
            
            print(f"\n[{i}/{len(image_files)}] 处理: {img_file.name}")
            
            success, _, result = await remove_bg_file_single(
                client, str(img_file), str(output_file), model
            )
            
            if success:
                success_count += 1
                print(f"   ✅ 成功 - 耗时: {result.get('processing_time', 'N/A')}s")
            else:
                failed_files.append(img_file.name)
                print(f"   ❌ 失败 - {result.get('error', 'Unknown error')}")
    
    end_time = time.time()
    total_time = round(end_time - start_time, 2)
    
    print(f"\n{'='*60}")
    print(f"批量处理完成")
    print(f"{'='*60}")
    print(f"总文件数: {len(image_files)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(failed_files)}")
    print(f"总耗时: {total_time}s")
    
    if failed_files:
        print(f"\n失败的文件:")
        for f in failed_files:
            print(f"   - {f}")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("文件进文件出 - 批量处理测试")
    print("="*60)
    
    # 方式1: 并发批量处理（推荐，更快）
    await batch_process_files(INPUT_DIR, OUTPUT_DIR, MODEL)
    
    # 方式2: 顺序批量处理（带详细进度）
    # await batch_process_with_progress(INPUT_DIR, OUTPUT_DIR + "_seq", MODEL)


if __name__ == "__main__":
    asyncio.run(main())
