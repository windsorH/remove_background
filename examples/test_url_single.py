"""URL进URL出 - 单条处理示例"""
import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

# 测试配置
TEST_IMAGE_URL = "https://raw.githubusercontent.com/danielgatis/rembg/master/examples/girl.jpg"
OUTPUT_PATH = "url_output.png"
MODEL = "u2net_human_seg"  # 模型选择


async def remove_bg_url_single(
    image_url: str,
    output_path: str,
    model: str = "u2net",
    output_type: str = "file"
):
    """
    单URL背景移除 - URL进URL出
    
    Args:
        image_url: 输入图像URL
        output_path: 输出路径
        model: 使用的模型名称
        output_type: 输出类型 (file/oss)
    """
    print(f"{'='*60}")
    print(f"单URL处理")
    print(f"{'='*60}")
    print(f"输入URL: {image_url}")
    print(f"输出路径: {output_path}")
    print(f"使用模型: {model}")
    print(f"输出类型: {output_type}")
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "image_url": image_url,
                "output_type": output_type,
                "output_path": output_path,
                "model": model,
                "stream": False
            }
            
            print(f"\n正在发送请求...")
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
                    print(f"   输出路径: {result['data']['path']}")
                    print(f"   图片尺寸: {result['data']['width']}x{result['data']['height']}")
                    print(f"   处理时间: {result['data']['processing_time']}s")
                    return True, result["data"]
                else:
                    print(f"❌ 处理失败: {result}")
                    return False, None
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False, None


async def remove_bg_url_single_stream(
    image_url: str,
    output_path: str,
    model: str = "u2net",
    output_type: str = "file"
):
    """
    单URL背景移除 - 流式响应
    
    Args:
        image_url: 输入图像URL
        output_path: 输出路径
        model: 使用的模型名称
        output_type: 输出类型 (file/oss)
    """
    print(f"\n{'='*60}")
    print(f"单URL处理 - 流式响应")
    print(f"{'='*60}")
    print(f"输入URL: {image_url}")
    print(f"输出路径: {output_path}")
    print(f"使用模型: {model}")
    
    async with httpx.AsyncClient() as client:
        try:
            payload = {
                "image_url": image_url,
                "output_type": output_type,
                "output_path": output_path,
                "model": model,
                "stream": True
            }
            
            print(f"\n正在发送请求（流式）...")
            async with client.stream(
                "POST",
                f"{BASE_URL}/v1/bg/remove/url",
                json=payload,
                timeout=120.0
            ) as response:
                if response.status_code == 200:
                    print(f"✅ 收到流式响应:")
                    async for line in response.aiter_lines():
                        if line:
                            event = json.loads(line)
                            event_type = event.get("type", "unknown")
                            
                            if event_type == "start":
                                print(f"   🚀 开始处理...")
                            elif event_type == "progress":
                                step = event.get("step", "")
                                percent = event.get("percent", 0)
                                message = event.get("message", "")
                                print(f"   ⏳ {message} ({percent}%)")
                            elif event_type == "complete":
                                result = event.get("result", {})
                                print(f"   ✅ 处理完成!")
                                print(f"      输出URL: {result.get('url')}")
                                print(f"      输出路径: {result.get('path')}")
                                print(f"      图片尺寸: {result.get('width')}x{result.get('height')}")
                                print(f"      处理时间: {result.get('processing_time')}s")
                                return True, result
                            elif event_type == "error":
                                print(f"   ❌ 错误: {event.get('error')}")
                                return False, None
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    return False, None
                    
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False, None


async def test_anime_url():
    """测试动漫图片URL"""
    # 动漫图片示例URL
    anime_url = "https://example.com/anime_character.jpg"  # 请替换为实际的动漫图片URL
    
    print(f"\n{'='*60}")
    print(f"动漫图片URL测试")
    print(f"{'='*60}")
    
    await remove_bg_url_single(
        anime_url,
        "anime_output.png",
        model="isnet-anime"
    )


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("URL进URL出 - 单条处理测试")
    print("="*60)
    
    # 测试普通响应
    await remove_bg_url_single(TEST_IMAGE_URL, OUTPUT_PATH, MODEL)
    
    # 测试流式响应
    # await remove_bg_url_single_stream(TEST_IMAGE_URL, "stream_" + OUTPUT_PATH, MODEL)
    
    # 测试动漫模型
    # await test_anime_url()


if __name__ == "__main__":
    asyncio.run(main())
