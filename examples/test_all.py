"""综合测试脚本 - 测试所有功能"""
import httpx
import asyncio
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"


async def test_health():
    """测试服务健康状态"""
    print(f"\n{'='*60}")
    print("1. 健康检查")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=10.0)
            if response.status_code == 200:
                print(f"✅ 服务正常运行")
                print(f"   响应: {response.json()}")
                return True
            else:
                print(f"❌ 服务异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            print(f"   请确保服务已启动: python -m src.bg_remover.main")
            return False


async def test_models_api():
    """测试模型列表API"""
    print(f"\n{'='*60}")
    print("2. 模型列表API测试")
    print(f"{'='*60}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/v1/models", timeout=10.0)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    models = result.get("data", [])
                    print(f"✅ 获取模型列表成功")
                    print(f"\n可用模型 ({len(models)}个):")
                    for model in models:
                        print(f"   - {model['name']}: {model['description']}")
                        print(f"     适用场景: {model['use_case']}")
                    return True
                else:
                    print(f"❌ 获取失败: {result}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False


async def test_model_info():
    """测试模型详情API"""
    print(f"\n{'='*60}")
    print("3. 模型详情API测试")
    print(f"{'='*60}")
    
    models_to_test = ["u2net", "isnet-anime", "u2net_human_seg"]
    
    async with httpx.AsyncClient() as client:
        for model in models_to_test:
            try:
                response = await client.get(
                    f"{BASE_URL}/v1/models/{model}/info",
                    timeout=10.0
                )
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        info = result.get("data", {})
                        print(f"✅ {model}: {info.get('description')}")
                    else:
                        print(f"❌ {model}: 获取失败")
                else:
                    print(f"❌ {model}: HTTP {response.status_code}")
            except Exception as e:
                print(f"❌ {model}: {e}")
    
    return True


async def test_file_single():
    """测试单文件处理"""
    print(f"\n{'='*60}")
    print("4. 单文件处理测试")
    print(f"{'='*60}")
    
    test_file = "./test_input.png"
    
    if not Path(test_file).exists():
        print(f"⚠️  测试文件不存在: {test_file}")
        print(f"   跳过此测试")
        return None
    
    async with httpx.AsyncClient() as client:
        with open(test_file, "rb") as f:
            files = {"file": ("test.png", f, "image/png")}
            data = {
                "output_type": "file",
                "output_path": "test_output_single.png",
                "model": "u2net",
                "stream": "false"
            }
            
            try:
                response = await client.post(
                    f"{BASE_URL}/v1/bg/remove/file",
                    files=files,
                    data=data,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ 单文件处理成功")
                        print(f"   输出: {result['data']['path']}")
                        print(f"   尺寸: {result['data']['width']}x{result['data']['height']}")
                        print(f"   耗时: {result['data']['processing_time']}s")
                        return True
                    else:
                        print(f"❌ 处理失败: {result}")
                        return False
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ 异常: {e}")
                return False


async def test_url_single():
    """测试单URL处理"""
    print(f"\n{'='*60}")
    print("5. 单URL处理测试")
    print(f"{'='*60}")
    
    # 使用一个示例URL
    test_url = "https://raw.githubusercontent.com/danielgatis/rembg/master/examples/girl.jpg"
    
    async with httpx.AsyncClient() as client:
        payload = {
            "image_url": test_url,
            "output_type": "file",
            "output_path": "test_url_output.png",
            "model": "u2net_human_seg",
            "stream": False
        }
        
        try:
            response = await client.post(
                f"{BASE_URL}/v1/bg/remove/url",
                json=payload,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ URL处理成功")
                    print(f"   输出: {result['data']['url']}")
                    print(f"   尺寸: {result['data']['width']}x{result['data']['height']}")
                    print(f"   耗时: {result['data']['processing_time']}s")
                    return True
                else:
                    print(f"❌ 处理失败: {result}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   可能原因: 无法访问外部URL或网络问题")
                return False
        except Exception as e:
            print(f"❌ 异常: {e}")
            return False


async def test_anime_model():
    """测试动漫模型"""
    print(f"\n{'='*60}")
    print("6. 动漫模型测试")
    print(f"{'='*60}")
    
    test_file = "./test_anime/anime.png"
    
    if not Path(test_file).exists():
        print(f"⚠️  动漫测试文件不存在: {test_file}")
        print(f"   跳过此测试")
        return None
    
    async with httpx.AsyncClient() as client:
        with open(test_file, "rb") as f:
            files = {"file": ("anime.png", f, "image/png")}
            data = {
                "output_type": "file",
                "output_path": "test_anime_output.png",
                "model": "isnet-anime",
                "stream": "false"
            }
            
            try:
                response = await client.post(
                    f"{BASE_URL}/v1/bg/remove/file",
                    files=files,
                    data=data,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print(f"✅ 动漫模型处理成功")
                        print(f"   输出: {result['data']['path']}")
                        print(f"   尺寸: {result['data']['width']}x{result['data']['height']}")
                        print(f"   耗时: {result['data']['processing_time']}s")
                        return True
                    else:
                        print(f"❌ 处理失败: {result}")
                        return False
                else:
                    print(f"❌ 请求失败: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ 异常: {e}")
                return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("综合测试 - 背景移除服务")
    print("="*60)
    
    results = {}
    
    # 1. 健康检查
    results["health"] = await test_health()
    
    # 如果健康检查失败，停止后续测试
    if not results["health"]:
        print(f"\n{'='*60}")
        print("❌ 服务未启动，停止测试")
        print(f"{'='*60}")
        print("请启动服务: python -m src.bg_remover.main")
        return results
    
    # 2. 模型列表API
    results["models_api"] = await test_models_api()
    
    # 3. 模型详情API
    results["model_info"] = await test_model_info()
    
    # 4. 单文件处理
    results["file_single"] = await test_file_single()
    
    # 5. 单URL处理
    results["url_single"] = await test_url_single()
    
    # 6. 动漫模型
    results["anime_model"] = await test_anime_model()
    
    return results


async def main():
    """主函数"""
    results = await run_all_tests()
    
    # 打印测试总结
    print(f"\n{'='*60}")
    print("测试总结")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r is True)
    skipped_tests = sum(1 for r in results.values() if r is None)
    failed_tests = sum(1 for r in results.values() if r is False)
    
    print(f"\n总测试数: {total_tests}")
    print(f"✅ 通过: {passed_tests}")
    print(f"⚠️  跳过: {skipped_tests}")
    print(f"❌ 失败: {failed_tests}")
    
    print(f"\n详细结果:")
    for test_name, result in results.items():
        status = "✅ 通过" if result is True else ("⚠️  跳过" if result is None else "❌ 失败")
        print(f"   {test_name}: {status}")
    
    # 返回退出码
    if failed_tests > 0:
        print(f"\n❌ 部分测试失败")
        sys.exit(1)
    else:
        print(f"\n✅ 所有测试通过")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
