"""URL进URL出 - 批量处理示例"""
import httpx
import asyncio
from typing import List, Tuple
import time

BASE_URL = "http://localhost:8000"

# 测试配置
MODEL = "u2net_human_seg"  # 模型选择
CONCURRENT_LIMIT = 3  # 并发数限制

# 测试URL列表（请替换为实际的图片URL）
TEST_URLS = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg",
    "https://example.com/image4.jpg",
    "https://example.com/image5.jpg",
]

# 动漫图片URL列表（用于测试动漫模型）
ANIME_URLS = [
    "https://example.com/anime1.jpg",
    "https://example.com/anime2.jpg",
    "https://example.com/anime3.jpg",
]


async def remove_bg_url_single(
    client: httpx.AsyncClient,
    image_url: str,
    output_path: str,
    model: str = "u2net",
    output_type: str = "file"
) -> Tuple[bool, str, dict]:
    """
    单URL背景移除
    
    Returns:
        (成功状态, 输入URL, 结果信息)
    """
    try:
        payload = {
            "image_url": image_url,
            "output_type": output_type,
            "output_path": output_path,
            "model": model,
            "stream": False
        }
        
        response = await client.post(
            f"{BASE_URL}/v1/bg/remove/url",
            json=payload,
            timeout=120.0
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return True, image_url, result["data"]
            else:
                return False, image_url, {"error": result}
        else:
            return False, image_url, {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        return False, image_url, {"error": str(e)}


async def process_batch_with_semaphore(
    client: httpx.AsyncClient,
    tasks: List[Tuple[str, str, str, str]],
    max_concurrent: int = 3
) -> List[Tuple[bool, str, dict]]:
    """
    使用信号量控制并发数批量处理
    
    Args:
        client: HTTP客户端
        tasks: 任务列表 [(image_url, output_path, model, output_type), ...]
        max_concurrent: 最大并发数
    
    Returns:
        结果列表
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_with_limit(image_url: str, output_path: str, model: str, output_type: str):
        async with semaphore:
            result = await remove_bg_url_single(client, image_url, output_path, model, output_type)
            # 打印进度
            status = "✅" if result[0] else "❌"
            url_short = image_url[:50] + "..." if len(image_url) > 50 else image_url
            print(f"   {status} {url_short}")
            return result
    
    # 创建所有任务
    coroutines = [
        process_with_limit(image_url, output_path, model, output_type)
        for image_url, output_path, model, output_type in tasks
    ]
    
    # 并发执行
    results = await asyncio.gather(*coroutines, return_exceptions=True)
    
    # 处理异常结果
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            image_url = tasks[i][0]
            processed_results.append((False, image_url, {"error": str(result)}))
        else:
            processed_results.append(result)
    
    return processed_results


async def batch_process_urls(
    urls: List[str],
    output_prefix: str = "output",
    model: str = "u2net",
    output_type: str = "file"
):
    """
    批量处理URL列表
    
    Args:
        urls: URL列表
        output_prefix: 输出文件名前缀
        model: 使用的模型
        output_type: 输出类型
    """
    print(f"\n{'='*60}")
    print(f"批量URL处理")
    print(f"{'='*60}")
    print(f"URL数量: {len(urls)}")
    print(f"使用模型: {model}")
    print(f"并发限制: {CONCURRENT_LIMIT}")
    
    if not urls:
        print(f"❌ 错误: URL列表为空")
        return
    
    # 准备任务列表
    tasks = []
    for i, url in enumerate(urls):
        output_path = f"{output_prefix}_{i+1:03d}.png"
        tasks.append((url, output_path, model, output_type))
    
    print(f"\n开始处理...\n")
    
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
    print(f"总URL数: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"总耗时: {total_time}s")
    if len(results) > 0:
        print(f"平均每个: {round(total_time/len(results), 2)}s")
    
    # 显示失败的URL
    failed_urls = [r[1] for r in results if not r[0]]
    if failed_urls:
        print(f"\n失败的URL:")
        for url in failed_urls:
            print(f"   - {url[:60]}...")
    
    # 显示成功的结果
    print(f"\n成功的结果:")
    for success, url, data in results:
        if success:
            url_short = url[:40] + "..." if len(url) > 40 else url
            print(f"   ✅ {url_short}")
            print(f"      输出: {data.get('url', 'N/A')}")
            print(f"      尺寸: {data.get('width')}x{data.get('height')}")
            print(f"      耗时: {data.get('processing_time')}s")


async def batch_process_with_progress(
    urls: List[str],
    output_prefix: str = "output",
    model: str = "u2net",
    output_type: str = "file"
):
    """
    批量处理带进度显示（顺序处理）
    """
    print(f"\n{'='*60}")
    print(f"批量URL处理 - 顺序模式")
    print(f"{'='*60}")
    print(f"URL数量: {len(urls)}")
    print(f"使用模型: {model}")
    
    if not urls:
        print(f"❌ 错误: URL列表为空")
        return
    
    # 顺序处理
    start_time = time.time()
    success_count = 0
    failed_urls = []
    results = []
    
    async with httpx.AsyncClient() as client:
        for i, url in enumerate(urls, 1):
            output_path = f"{output_prefix}_{i:03d}.png"
            
            print(f"\n[{i}/{len(urls)}] 处理: {url[:50]}...")
            
            success, _, result = await remove_bg_url_single(
                client, url, output_path, model, output_type
            )
            
            if success:
                success_count += 1
                results.append(result)
                print(f"   ✅ 成功")
                print(f"      输出: {result.get('url', 'N/A')}")
                print(f"      耗时: {result.get('processing_time', 'N/A')}s")
            else:
                failed_urls.append(url)
                print(f"   ❌ 失败 - {result.get('error', 'Unknown error')}")
    
    end_time = time.time()
    total_time = round(end_time - start_time, 2)
    
    print(f"\n{'='*60}")
    print(f"批量处理完成")
    print(f"{'='*60}")
    print(f"总URL数: {len(urls)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(failed_urls)}")
    print(f"总耗时: {total_time}s")
    
    if failed_urls:
        print(f"\n失败的URL:")
        for url in failed_urls:
            print(f"   - {url}")


async def batch_process_anime_urls():
    """批量处理动漫图片URL（使用isnet-anime模型）"""
    print(f"\n{'='*60}")
    print(f"动漫图片批量处理")
    print(f"{'='*60}")
    print(f"使用模型: isnet-anime (动漫专用)")
    
    # 使用示例URL或自定义URL
    urls = ANIME_URLS if ANIME_URLS[0].startswith("http") else [
        "https://raw.githubusercontent.com/example/anime1.jpg",
        "https://raw.githubusercontent.com/example/anime2.jpg",
    ]
    
    await batch_process_urls(urls, "anime_output", model="isnet-anime")


async def compare_models():
    """对比不同模型的效果"""
    test_url = TEST_URLS[0] if TEST_URLS[0].startswith("http") else "https://example.com/test.jpg"
    
    models_to_test = [
        ("u2net", "通用模型"),
        ("u2net_human_seg", "人像模型"),
        ("isnet-anime", "动漫模型"),
        ("birefnet-portrait", "高精度人像"),
    ]
    
    print(f"\n{'='*60}")
    print(f"模型效果对比测试")
    print(f"{'='*60}")
    print(f"测试URL: {test_url}")
    print(f"\n测试模型:")
    
    async with httpx.AsyncClient() as client:
        for model, desc in models_to_test:
            print(f"\n{'-'*40}")
            print(f"模型: {model} ({desc})")
            print(f"{'-'*40}")
            
            output_path = f"compare_{model}.png"
            
            start_time = time.time()
            success, _, result = await remove_bg_url_single(
                client, test_url, output_path, model
            )
            elapsed = round(time.time() - start_time, 2)
            
            if success:
                print(f"✅ 成功")
                print(f"   输出: {result.get('url')}")
                print(f"   尺寸: {result.get('width')}x{result.get('height')}")
                print(f"   API耗时: {result.get('processing_time')}s")
                print(f"   总耗时: {elapsed}s")
            else:
                print(f"❌ 失败: {result.get('error')}")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("URL进URL出 - 批量处理测试")
    print("="*60)
    
    # 方式1: 并发批量处理（推荐，更快）
    # 请替换为实际的URL
    # await batch_process_urls(TEST_URLS, "batch_output", MODEL)
    
    # 方式2: 顺序批量处理（带详细进度）
    # await batch_process_with_progress(TEST_URLS, "seq_output", MODEL)
    
    # 方式3: 动漫图片批量处理
    # await batch_process_anime_urls()
    
    # 方式4: 模型对比测试
    # await compare_models()
    
    print("\n⚠️  提示: 请修改脚本中的 TEST_URLS 为实际的图片URL后再运行")
    print("示例URL格式:")
    print("  - https://example.com/image.jpg")
    print("  - https://raw.githubusercontent.com/.../image.png")


if __name__ == "__main__":
    asyncio.run(main())
