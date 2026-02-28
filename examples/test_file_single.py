"""文件进文件出 - 单条处理示例"""
import httpx
import asyncio
import os
from pathlib import Path

BASE_URL = "http://localhost:8000"

# 测试配置
INPUT_FILE = "test_input.png"  # 输入文件路径
OUTPUT_FILE = "test_output.png"  # 输出文件路径
MODEL = "isnet-anime"  # 模型选择: u2net, u2net_human_seg, isnet-anime, birefnet-portrait


async def remove_bg_file_single(
    input_path: str,
    output_path: str,
    model: str = "u2net"
):
    """
    单文件背景移除 - 文件进文件出
    
    Args:
        input_path: 输入图像文件路径
        output_path: 输出图像文件路径
        model: 使用的模型名称
    """
    print(f"="*60)
    print(f"单文件处理")
    print(f"="*60)
    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"使用模型: {model}")
    
    # 检查输入文件是否存在
    if not Path(input_path).exists():
        print(f"❌ 错误: 输入文件不存在: {input_path}")
        return False
    
    async with httpx.AsyncClient() as client:
        try:
            with open(input_path, "rb") as f:
                files = {"file": (Path(input_path).name, f, "image/png")}
                data = {
                    "output_type": "file",
                    "output_path": output_path,
                    "model": model,
                    "stream": "false"
                }
                
                print(f"\n正在发送请求...")
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
                        return True
                    else:
                        print(f"❌ 处理失败: {result}")
                        return False
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    print(f"   错误信息: {response.text}")
                    return False
                    
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False


async def remove_bg_file_single_stream(
    input_path: str,
    output_path: str,
    model: str = "u2net"
):
    """
    单文件背景移除 - 流式响应
    
    Args:
        input_path: 输入图像文件路径
        output_path: 输出图像文件路径
        model: 使用的模型名称
    """
    print(f"\n{'='*60}")
    print(f"单文件处理 - 流式响应")
    print(f"{'='*60}")
    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"使用模型: {model}")
    
    # 检查输入文件是否存在
    if not Path(input_path).exists():
        print(f"❌ 错误: 输入文件不存在: {input_path}")
        return False
    
    async with httpx.AsyncClient() as client:
        try:
            with open(input_path, "rb") as f:
                files = {"file": (Path(input_path).name, f, "image/png")}
                data = {
                    "output_type": "file",
                    "output_path": output_path,
                    "model": model,
                    "stream": "true"
                }
                
                print(f"\n正在发送请求（流式）...")
                async with client.stream(
                    "POST",
                    f"{BASE_URL}/v1/bg/remove/file",
                    files=files,
                    data=data,
                    timeout=120.0
                ) as response:
                    if response.status_code == 200:
                        print(f"✅ 收到流式响应:")
                        async for line in response.aiter_lines():
                            if line:
                                import json
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
                                    print(f"      输出路径: {result.get('path')}")
                                    print(f"      图片尺寸: {result.get('width')}x{result.get('height')}")
                                    print(f"      处理时间: {result.get('processing_time')}s")
                                    return True
                                elif event_type == "error":
                                    print(f"   ❌ 错误: {event.get('error')}")
                                    return False
                    else:
                        print(f"❌ 请求失败: {response.status_code}")
                        return False
                        
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("文件进文件出 - 单条处理测试")
    print("="*60)
    
    # 测试普通响应
    await remove_bg_file_single(INPUT_FILE, OUTPUT_FILE, MODEL)
    
    # 测试流式响应
    # await remove_bg_file_single_stream(INPUT_FILE, "stream_" + OUTPUT_FILE, MODEL)


if __name__ == "__main__":
    asyncio.run(main())
