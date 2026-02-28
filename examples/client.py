"""客户端示例"""
import httpx
import json
import asyncio


BASE_URL = "http://localhost:8000"


async def health_check():
    """健康检查"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print("Health:", response.json())


async def remove_bg_url_stream():
    """流式移除URL图像背景"""
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{BASE_URL}/v1/bg/remove/url",
            json={
                "image_url": "https://example.com/image.jpg",
                "output_type": "file",
                "output_path": "output.png",
                "stream": True
            }
        ) as response:
            print("\n流式响应:")
            async for line in response.aiter_lines():
                if line:
                    event = json.loads(line)
                    print(f"  {event}")


async def remove_bg_url_sync():
    """非流式移除URL图像背景"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/v1/bg/remove/url",
            json={
                "image_url": "https://example.com/image.jpg",
                "output_type": "file",
                "output_path": "output.png",
                "stream": False
            }
        )
        print("\n非流式响应:")
        print(response.json())


async def remove_bg_file(file_path: str):
    """上传文件移除背景"""
    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            files = {"file": ("input.png", f, "image/png")}
            data = {
                "output_type": "file",
                "output_path": "output.png",
                "stream": "false"
            }
            response = await client.post(
                f"{BASE_URL}/v1/bg/remove/file",
                files=files,
                data=data
            )
        print("\n文件上传响应:")
        print(response.json())


async def main():
    """主函数"""
    await health_check()
    # await remove_bg_url_stream()
    # await remove_bg_url_sync()


if __name__ == "__main__":
    asyncio.run(main())
