"""动漫专用模型测试 - isnet-anime"""
import httpx
import asyncio
from pathlib import Path

BASE_URL = "http://localhost:8000"

# 动漫图片测试配置
ANIME_TEST_IMAGES = [
    # 请替换为实际的动漫图片路径或URL
    "./test_anime/image1.png",
    "./test_anime/image2.jpg",
    "./test_anime/image3.png",
]

ANIME_TEST_URLS = [
    # 请替换为实际的动漫图片URL
    "https://example.com/anime1.jpg",
    "https://example.com/anime2.jpg",
]


async def test_anime_model_file():
    """测试动漫模型 - 文件输入"""
    print(f"\n{'='*60}")
    print(f"动漫模型测试 - 文件输入")
    print(f"{'='*60}")
    print(f"使用模型: isnet-anime (动漫专用)")
    
    input_file = "./test_anime/anime_character.png"
    output_file = "./test_output/anime_result.png"
    
    # 检查输入文件
    if not Path(input_file).exists():
        print(f"⚠️  示例文件不存在: {input_file}")
        print(f"   请准备动漫图片后测试")
        return
    
    async with httpx.AsyncClient() as client:
        with open(input_file, "rb") as f:
            files = {"file": (Path(input_file).name, f, "image/png")}
            data = {
                "output_type": "file",
                "output_path": output_file,
                "model": "isnet-anime",  # 使用动漫专用模型
                "stream": "false"
            }
            
            print(f"\n输入文件: {input_file}")
            print(f"输出文件: {output_file}")
            print(f"正在处理...")
            
            response = await client.post(
                f"{BASE_URL}/v1/bg/remove/file",
                files=files,
                data=data,
                timeout=120.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ 处理成功!")
                    print(f"   输出路径: {result['data']['path']}")
                    print(f"   图片尺寸: {result['data']['width']}x{result['data']['height']}")
                    print(f"   处理时间: {result['data']['processing_time']}s")
                else:
                    print(f"❌ 处理失败: {result}")
            else:
                print(f"❌ 请求失败: {response.status_code}")


async def test_anime_model_url():
    """测试动漫模型 - URL输入"""
    print(f"\n{'='*60}")
    print(f"动漫模型测试 - URL输入")
    print(f"{'='*60}")
    print(f"使用模型: isnet-anime (动漫专用)")
    
    image_url = ANIME_TEST_URLS[0] if ANIME_TEST_URLS[0].startswith("http") else None
    
    if not image_url:
        print(f"⚠️  请配置实际的动漫图片URL后再测试")
        return
    
    async with httpx.AsyncClient() as client:
        payload = {
            "image_url": image_url,
            "output_type": "file",
            "output_path": "anime_url_output.png",
            "model": "isnet-anime",
            "stream": False
        }
        
        print(f"\n输入URL: {image_url}")
        print(f"正在处理...")
        
        response = await client.post(
            f"{BASE_URL}/v1/bg/remove/url",
            json=payload,
            timeout=120.0
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ 处理成功!")
                print(f"   输出URL: {result['data']['url']}")
                print(f"   图片尺寸: {result['data']['width']}x{result['data']['height']}")
                print(f"   处理时间: {result['data']['processing_time']}s")
            else:
                print(f"❌ 处理失败: {result}")
        else:
            print(f"❌ 请求失败: {response.status_code}")


async def compare_anime_vs_general():
    """对比动漫模型和通用模型的效果"""
    print(f"\n{'='*60}")
    print(f"动漫模型 vs 通用模型 效果对比")
    print(f"{'='*60}")
    
    # 测试文件
    test_file = "./test_anime/anime_character.png"
    
    if not Path(test_file).exists():
        print(f"⚠️  示例文件不存在: {test_file}")
        print(f"   请准备动漫图片后测试")
        return
    
    models_to_compare = [
        ("u2net", "通用模型"),
        ("u2net_human_seg", "人像模型"),
        ("isnet-anime", "动漫专用模型⭐"),
        ("birefnet-portrait", "高精度人像"),
    ]
    
    print(f"\n测试文件: {test_file}")
    print(f"\n对比模型:")
    
    async with httpx.AsyncClient() as client:
        for model, desc in models_to_compare:
            print(f"\n{'-'*50}")
            print(f"模型: {model}")
            print(f"描述: {desc}")
            print(f"{'-'*50}")
            
            output_path = f"./test_output/compare_{model}.png"
            
            with open(test_file, "rb") as f:
                files = {"file": (Path(test_file).name, f, "image/png")}
                data = {
                    "output_type": "file",
                    "output_path": output_path,
                    "model": model,
                    "stream": "false"
                }
                
                import time
                start = time.time()
                
                response = await client.post(
                    f"{BASE_URL}/v1/bg/remove/file",
                    files=files,
                    data=data,
                    timeout=120.0
                )
                
                elapsed = round(time.time() - start, 2)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ 成功")
                        print(f"   输出: {output_path}")
                        print(f"   API耗时: {result['data']['processing_time']}s")
                        print(f"   总耗时: {elapsed}s")
                    else:
                        print(f"❌ 失败: {result}")
                else:
                    print(f"❌ 请求失败: {response.status_code}")
    
    print(f"\n{'='*60}")
    print(f"对比完成!")
    print(f"{'='*60}")
    print(f"请查看 ./test_output/ 目录下的输出文件:")
    for model, _ in models_to_compare:
        print(f"  - compare_{model}.png")
    print(f"\n💡 建议: 动漫图片使用 isnet-anime 模型效果最佳")


async def batch_process_anime_files():
    """批量处理动漫图片文件"""
    print(f"\n{'='*60}")
    print(f"动漫图片批量处理")
    print(f"{'='*60}")
    print(f"使用模型: isnet-anime (动漫专用)")
    
    input_dir = Path("./test_anime")
    output_dir = Path("./test_output/anime_batch")
    
    if not input_dir.exists():
        print(f"⚠️  输入目录不存在: {input_dir}")
        print(f"   请创建目录并放入动漫图片后测试")
        return
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有图像文件
    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp"]:
        image_files.extend(input_dir.glob(ext))
    
    if not image_files:
        print(f"⚠️  未找到图像文件")
        return
    
    print(f"\n找到 {len(image_files)} 个图像文件")
    print(f"开始批量处理...\n")
    
    success_count = 0
    
    async with httpx.AsyncClient() as client:
        for i, img_file in enumerate(image_files, 1):
            output_file = output_dir / f"{img_file.stem}_nobg.png"
            
            print(f"[{i}/{len(image_files)}] {img_file.name}...", end=" ")
            
            with open(img_file, "rb") as f:
                files = {"file": (img_file.name, f, "image/png")}
                data = {
                    "output_type": "file",
                    "output_path": str(output_file),
                    "model": "isnet-anime",
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
                        print(f"✅ 成功 ({result['data']['processing_time']}s)")
                        success_count += 1
                    else:
                        print(f"❌ 失败")
                else:
                    print(f"❌ 失败 ({response.status_code})")
    
    print(f"\n{'='*60}")
    print(f"批量处理完成: {success_count}/{len(image_files)}")
    print(f"{'='*60}")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("动漫专用模型测试 - isnet-anime")
    print("="*60)
    print("\n这个脚本专门测试动漫/卡通人物的背景移除效果")
    print("使用 isnet-anime 模型，针对动漫图像优化")
    
    # 创建测试目录
    Path("./test_anime").mkdir(exist_ok=True)
    Path("./test_output").mkdir(exist_ok=True)
    
    # 选择要运行的测试
    # await test_anime_model_file()
    # await test_anime_model_url()
    # await compare_anime_vs_general()
    # await batch_process_anime_files()
    
    print("\n" + "="*60)
    print("使用说明")
    print("="*60)
    print("\n1. 准备动漫图片:")
    print("   - 放入 ./test_anime/ 目录")
    print("   - 支持格式: png, jpg, jpeg, webp")
    print("\n2. 修改脚本取消注释要运行的测试函数")
    print("\n3. 运行脚本:")
    print("   python examples/test_anime_model.py")
    print("\n4. 查看结果:")
    print("   - 单张处理结果: ./test_output/anime_result.png")
    print("   - 批量处理结果: ./test_output/anime_batch/")
    print("   - 对比结果: ./test_output/compare_*.png")


if __name__ == "__main__":
    asyncio.run(main())
