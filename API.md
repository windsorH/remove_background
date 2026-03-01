# API 接口文档

本文档面向调用背景移除服务的开发人员，提供完整的 API 接口说明。

## 📋 目录

- [基础信息](#基础信息)
- [认证方式](#认证方式)
- [错误处理](#错误处理)
- [接口列表](#接口列表)
- [代码示例](#代码示例)
- [最佳实践](#最佳实践)

---

## 基础信息

### 服务地址

```
http://localhost:8000
```

### 请求格式

- 请求体编码：`application/json` 或 `multipart/form-data`
- 响应体编码：`application/json` 或 `application/x-ndjson`（流式）
- 字符编码：UTF-8

### 支持的模型

| 模型名称 | 适用场景 | 文件大小 | 说明 |
|---------|---------|---------|------|
| `u2net` | 通用场景 | ~168MB | 默认模型，通用背景移除 |
| `u2net_human_seg` | 人像照片 | ~168MB | 专门针对人像分割优化 |
| `isnet-anime` | 动漫/卡通 | ~176MB | ⭐ **动漫/卡通人物专用模型** |
| `birefnet-portrait` | 高精度人像 | ~220MB | 高精度人像分割 |

### 限制说明

| 限制项 | 默认值 | 说明 |
|--------|--------|------|
| 最大文件大小 | 10MB | 上传文件大小限制 |
| 最大并发请求 | 5 | 超出会排队等待 |
| 请求超时时间 | 120秒 | 处理超时返回 504 |

---

## 认证方式

当前版本无需认证，直接调用即可。

---

## 错误处理

### HTTP 状态码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 | 请求成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式 |
| 413 | 文件过大 | 压缩图片或调整配置 |
| 500 | 服务器内部错误 | 查看错误信息，稍后重试 |
| 504 | 请求超时 | 减小图片尺寸或增加超时时间 |

### 错误响应格式

**非流式响应**

```json
{
    "success": false,
    "error": "错误描述信息",
    "error_code": "ERROR_CODE",
    "data": null
}
```

**流式响应 (NDJSON)**

```
{"type": "error", "success": false, "error": "错误描述信息", "error_code": "ERROR_CODE"}
```

### 错误码说明

| 错误码 | HTTP 状态码 | 说明 | 处理建议 |
|--------|-------------|------|----------|
| `IMAGE_LOAD_ERROR` | 400 | 图像加载失败 | 检查 URL 是否可访问或文件是否损坏 |
| `IMAGE_PROCESS_ERROR` | 500 | 图像处理失败 | 检查图像格式是否支持，稍后重试 |
| `MODEL_NOT_FOUND` | 404 | 模型不存在 | 检查模型名称是否正确 |
| `OSS_CONFIG_ERROR` | 500 | OSS 未配置 | 检查 OSS 配置或改用 file 输出类型 |
| `FILE_SIZE_EXCEEDED` | 413 | 文件大小超过限制 | 压缩图片或调整配置 |
| `TIMEOUT` | 504 | 请求超时 | 减小图片尺寸或增加超时时间 |
| - | 500 | 服务器内部错误 | 查看错误信息，稍后重试 |

---

## 接口列表

### 1. 健康检查

检查服务运行状态，获取配置信息和已预热模型列表。

**请求**

```http
GET /health
```

**响应**

```json
{
    "status": "ok",
    "version": "0.1.0",
    "timestamp": "2024-01-01T00:00:00",
    "config": {
        "max_concurrent_requests": 5,
        "request_timeout_seconds": 120,
        "thread_pool_workers": 4,
        "max_file_size_mb": 10,
        "enable_model_warmup": true
    },
    "models": {
        "available": ["u2net", "u2net_human_seg", "isnet-anime", "birefnet-portrait"],
        "warmed": ["u2net", "u2net_human_seg"],
        "default": "u2net"
    }
}
```

**字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | 服务状态，ok 表示正常 |
| `version` | string | API 版本号 |
| `timestamp` | string | 服务器当前时间 |
| `config` | object | 服务配置信息 |
| `models.available` | array | 所有可用模型列表 |
| `models.warmed` | array | 已预热模型列表（响应更快） |
| `models.default` | string | 默认模型名称 |

---

### 2. 获取模型列表

获取所有可用的背景移除模型列表。

**请求**

```http
GET /v1/models
```

**响应**

```json
{
    "success": true,
    "data": [
        {
            "name": "u2net",
            "description": "通用模型（默认）",
            "use_case": "通用场景"
        },
        {
            "name": "u2net_human_seg",
            "description": "人像分割模型⭐",
            "use_case": "人像照片"
        },
        {
            "name": "isnet-anime",
            "description": "动漫专用模型⭐",
            "use_case": "动漫/卡通人物"
        },
        {
            "name": "birefnet-portrait",
            "description": "高精度人像模型⭐",
            "use_case": "高质量人像分割"
        }
    ]
}
```

---

### 3. 获取模型详情

获取指定模型的详细信息。

**请求**

```http
GET /v1/models/{model_name}/info
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model_name` | string | 是 | 模型名称 |

**响应**

```json
{
    "success": true,
    "data": {
        "name": "isnet-anime",
        "description": "动漫专用模型⭐",
        "use_case": "动漫/卡通人物"
    }
}
```

**错误响应**

```json
{
    "detail": "模型 'xxx' 不存在。可用模型: ['u2net', 'u2net_human_seg', 'isnet-anime', 'birefnet-portrait']"
}
```

---

### 4. URL 移除背景

从 URL 加载图像并移除背景。

**请求**

```http
POST /v1/bg/remove/url
Content-Type: application/json
```

**请求体参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `image_url` | string | 是 | - | 图像 URL，支持 http/https |
| `output_type` | string | 否 | file | 输出类型：`file` 或 `oss` |
| `output_path` | string | 是 | - | 输出路径（相对或绝对） |
| `model` | string | 否 | u2net | 模型名称，见支持的模型列表 |
| `stream` | boolean | 否 | false | 是否流式响应 |

**请求示例**

```json
{
    "image_url": "https://example.com/image.jpg",
    "output_type": "file",
    "output_path": "output/result.png",
    "model": "isnet-anime",
    "stream": false
}
```

**非流式响应**

```json
{
    "success": true,
    "data": {
        "url": "./output/output.png",
        "path": "output/result.png",
        "width": 512,
        "height": 512,
        "format": "PNG",
        "processing_time": 2.35
    }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 是否成功 |
| `data.url` | string | 输出文件 URL 或路径 |
| `data.path` | string | 输出路径 |
| `data.width` | integer | 输出图像宽度 |
| `data.height` | integer | 输出图像高度 |
| `data.format` | string | 输出格式，固定为 PNG |
| `data.processing_time` | float | 处理耗时（秒） |

**流式响应 (NDJSON)**

设置 `stream: true` 时，返回 NDJSON 格式的流式响应：

```
{"type": "start", "timestamp": 1700000000}
{"type": "progress", "step": "process", "percent": 30, "message": "正在移除背景..."}
{"type": "progress", "step": "output", "percent": 70, "message": "正在保存结果..."}
{"type": "complete", "result": {"url": "./output/output.png", "path": "output.png", ...}}
```

**流式事件类型**

| 类型 | 说明 | 字段 |
|------|------|------|
| `start` | 开始处理 | `timestamp` |
| `progress` | 进度更新 | `step`, `percent`, `message` |
| `complete` | 完成 | `result` |
| `error` | 错误 | `error` |

---

### 5. 文件上传移除背景

上传本地文件并移除背景。

**请求**

```http
POST /v1/bg/remove/file
Content-Type: multipart/form-data
```

**表单参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `file` | file | 是 | - | 图像文件，支持 PNG/JPG/JPEG/WEBP/BMP/TIFF/GIF |
| `output_type` | string | 否 | file | 输出类型：`file` 或 `oss` |
| `output_path` | string | 是 | - | 输出路径（相对或绝对） |
| `model` | string | 否 | u2net | 模型名称 |
| `stream` | boolean | 否 | false | 是否流式响应 |

**请求示例 (cURL)**

```bash
curl -X POST "http://localhost:8000/v1/bg/remove/file" \
  -F "file=@/path/to/image.jpg" \
  -F "output_type=file" \
  -F "output_path=output/result.png" \
  -F "model=isnet-anime" \
  -F "stream=false"
```

**响应**

与非流式 URL 接口相同。

---

## 代码示例

### Python 示例

#### 基础调用

```python
import httpx

async def remove_bg_from_url():
    """从 URL 移除背景"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/bg/remove/url",
            json={
                "image_url": "https://example.com/image.jpg",
                "output_type": "file",
                "output_path": "output.png",
                "model": "isnet-anime",
                "stream": False
            }
        )
        result = response.json()
        
        if result["success"]:
            print(f"处理成功: {result['data']['url']}")
            print(f"耗时: {result['data']['processing_time']}s")
        else:
            print(f"处理失败: {result.get('error')}")


async def remove_bg_from_file():
    """从文件移除背景"""
    async with httpx.AsyncClient() as client:
        with open("image.jpg", "rb") as f:
            files = {"file": ("image.jpg", f, "image/jpeg")}
            data = {
                "output_type": "file",
                "output_path": "output.png",
                "model": "u2net_human_seg",
                "stream": "false"
            }
            
            response = await client.post(
                "http://localhost:8000/v1/bg/remove/file",
                files=files,
                data=data
            )
            result = response.json()
            print(result)
```

#### 流式响应处理

```python
import httpx
import json

async def remove_bg_streaming():
    """流式处理，实时获取进度"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/bg/remove/url",
            json={
                "image_url": "https://example.com/image.jpg",
                "output_type": "file",
                "output_path": "output.png",
                "model": "isnet-anime",
                "stream": True  # 启用流式响应
            },
            timeout=120.0
        )
        
        # 逐行读取 NDJSON 流
        async for line in response.aiter_lines():
            if line:
                event = json.loads(line)
                event_type = event.get("type")
                
                if event_type == "start":
                    print("开始处理...")
                elif event_type == "progress":
                    print(f"进度: {event['percent']}% - {event['message']}")
                elif event_type == "complete":
                    result = event["result"]
                    print(f"完成! 输出: {result['url']}")
                    print(f"尺寸: {result['width']}x{result['height']}")
                    print(f"耗时: {result['processing_time']}s")
                elif event_type == "error":
                    print(f"错误: {event['error']}")
```

#### 批量处理

```python
import httpx
import asyncio
from pathlib import Path

async def batch_process(input_dir: str, output_dir: str):
    """批量处理文件夹中的图像"""   
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 获取所有图像文件
    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg"]:
        image_files.extend(input_path.glob(ext))
    
    # 限制并发数
    semaphore = asyncio.Semaphore(3)
    
    async def process_one(img_file: Path):
        async with semaphore:
            async with httpx.AsyncClient() as client:
                output_file = output_path / f"{img_file.stem}_nobg.png"
                
                with open(img_file, "rb") as f:
                    files = {"file": (img_file.name, f, "image/png")}
                    data = {
                        "output_type": "file",
                        "output_path": str(output_file),
                        "model": "isnet-anime",
                        "stream": "false"
                    }
                    
                    response = await client.post(
                        "http://localhost:8000/v1/bg/remove/file",
                        files=files,
                        data=data,
                        timeout=120.0
                    )
                    
                    result = response.json()
                    if result["success"]:
                        print(f"✅ {img_file.name} -> {output_file.name}")
                    else:
                        print(f"❌ {img_file.name}: {result.get('error')}")
    
    # 并发执行所有任务
    await asyncio.gather(*[process_one(f) for f in image_files])

# 使用
# asyncio.run(batch_process("./input", "./output"))
```

### JavaScript/TypeScript 示例

```typescript
async function removeBackground(imageUrl: string): Promise<void> {
    const response = await fetch('http://localhost:8000/v1/bg/remove/url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_url: imageUrl,
            output_type: 'file',
            output_path: 'output.png',
            model: 'isnet-anime',
            stream: false
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        console.log('处理成功:', result.data.url);
        console.log('耗时:', result.data.processing_time, 's');
    } else {
        console.error('处理失败:', result.error);
    }
}

// 流式响应处理
async function removeBackgroundStreaming(imageUrl: string): Promise<void> {
    const response = await fetch('http://localhost:8000/v1/bg/remove/url', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image_url: imageUrl,
            output_type: 'file',
            output_path: 'output.png',
            model: 'isnet-anime',
            stream: true
        })
    });
    
    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    
    if (!reader) return;
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const lines = decoder.decode(value).trim().split('\n');
        for (const line of lines) {
            const event = JSON.parse(line);
            
            switch (event.type) {
                case 'start':
                    console.log('开始处理...');
                    break;
                case 'progress':
                    console.log(`进度: ${event.percent}% - ${event.message}`);
                    break;
                case 'complete':
                    console.log('完成!', event.result);
                    break;
                case 'error':
                    console.error('错误:', event.error);
                    break;
            }
        }
    }
}
```

---

## 最佳实践

### 1. 模型选择

| 场景 | 推荐模型 | 说明 |
|------|----------|------|
| 动漫/卡通 | `isnet-anime` | 专门针对动漫优化 |
| 人像照片 | `u2net_human_seg` | 人像分割效果好 |
| 高精度人像 | `birefnet-portrait` | 质量最高但较慢 |
| 通用场景 | `u2net` | 速度快，通用性好 |

### 2. 性能优化

- **使用已预热模型**：调用 `/health` 查看 `models.warmed` 列表，优先使用已预热模型
- **启用流式响应**：大图片处理时使用流式响应，避免客户端超时
- **控制并发**：批量处理时控制并发数（建议 3-5），避免服务器过载
- **合理超时**：根据图片大小设置合理的超时时间

### 3. 错误处理

```python
import httpx

async def robust_remove_bg(image_url: str, max_retries: int = 3):
    """带重试的错误处理"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8000/v1/bg/remove/url",
                    json={
                        "image_url": image_url,
                        "output_type": "file",
                        "output_path": "output.png",
                        "model": "u2net"
                    },
                    timeout=120.0
                )
                
                result = response.json()
                
                if result.get("success"):
                    return result["data"]
                else:
                    error = result.get("error", "Unknown error")
                    if "timeout" in error.lower():
                        print(f"超时，重试 {attempt + 1}/{max_retries}")
                        continue
                    raise Exception(error)
                    
        except httpx.TimeoutException:
            print(f"请求超时，重试 {attempt + 1}/{max_retries}")
            if attempt == max_retries - 1:
                raise
        except Exception as e:
            print(f"错误: {e}")
            raise
    
    raise Exception("Max retries exceeded")
```

### 4. 文件上传注意事项

- 支持的格式：PNG, JPG, JPEG, WEBP, BMP, TIFF, GIF
- 文件大小限制：默认 10MB，超出会返回 413 错误
- 建议在上传前压缩大图片

### 5. 监控和调试

```python
# 检查服务状态
async def check_service():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/health")
        health = response.json()
        
        print(f"服务状态: {health['status']}")
        print(f"API 版本: {health['version']}")
        print(f"可用模型: {health['models']['available']}")
        print(f"已预热模型: {health['models']['warmed']}")
        print(f"并发限制: {health['config']['max_concurrent_requests']}")
        print(f"超时时间: {health['config']['request_timeout_seconds']}s")
```

---

## 更新日志

### v0.2.0

- 🏗️ **架构优化**
  - 重构核心处理逻辑，提取 `BgProcessor` 服务类
  - 简化导入逻辑，统一使用绝对导入
  - 使用 LRU 缓存限制模型实例数量（最多8个），防止内存泄漏
- 🛡️ **错误处理增强**
  - 新增自定义异常体系（`BgRemoverError` 基类及子类）
  - 统一错误响应格式，支持 `error_code` 字段
  - 细化错误类型：图像加载、处理、模型不存在、OSS配置、文件大小、超时等
- ⚙️ **配置改进**
  - 文件大小限制改为从配置动态读取
  - 移除硬编码配置项

### v0.1.0

- ✨ 初始版本发布
- 🚀 支持 4 种背景移除模型
- 📡 支持 URL 和文件上传
- 🔄 支持流式响应
- ⚡ 模型预热和线程池优化
- 🛡️ 并发控制和请求超时保护

---

如有问题，请参考 [README.md](./README.md) 或提交 Issue。
