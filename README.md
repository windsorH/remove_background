# 图像背景移除服务 (Background Remover Service)

基于 rembg 的 HTTP 流式服务，用于移除图像背景，生成透明 PNG 图像。支持多种模型，包括专门针对动漫/卡通人物优化的模型。

## ✨ 功能特性

- **多种输入方式**: 支持 URL 和本地上传
- **多种输出方式**: 支持本地文件和阿里云 OSS
- **流式响应**: 支持 NDJSON 格式的流式进度返回
- **多种模型**: 
  - `u2net` - 通用模型
  - `u2net_human_seg` - 人像分割模型
  - `isnet-anime` - ⭐ 动漫/卡通专用模型
  - `birefnet-portrait` - 高精度人像模型
- **批量处理**: 支持批量文件和 URL 处理
- **模型管理**: 模型文件本地存储，支持自定义路径

## 📁 项目结构

```
bg_remover/
├── src/bg_remover/
│   ├── main.py              # FastAPI 入口
│   ├── api/routes.py        # API 路由
│   ├── models/schemas.py    # 数据模型
│   ├── services/
│   │   ├── bg_remover.py    # 背景移除核心
│   │   ├── input_loader.py  # 输入加载
│   │   ├── output_saver.py  # 输出保存
│   │   └── oss_uploader.py  # OSS 上传
│   └── core/config.py       # 配置管理
├── examples/                # 测试脚本
│   ├── test_all.py          # 综合测试
│   ├── test_file_single.py  # 单文件测试
│   ├── test_file_batch.py   # 批量文件测试
│   ├── test_url_single.py   # 单 URL 测试
│   ├── test_url_batch.py    # 批量 URL 测试
│   └── test_anime_model.py  # 动漫模型测试
├── models/                  # 模型文件夹（自动创建）
├── start_server.py          # 启动脚本
├── download_models.py       # 模型下载脚本
├── requirements.txt         # 依赖
└── .env.example            # 环境变量示例
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载模型（可选）

```bash
python download_models.py
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，并填写配置：

```bash
# OSS 配置（可选）
OSS_ACCESS_KEY_ID=your-access-key-id
OSS_ACCESS_KEY_SECRET=your-access-key-secret
OSS_BUCKET=your-bucket-name
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com

# 服务器配置
HOST=0.0.0.0
PORT=8000
OUTPUT_DIR=./output

# 模型配置
MODEL_DIR=./models
DEFAULT_MODEL=u2net
```

### 4. 启动服务

```bash
python start_server.py
```

服务将在 http://localhost:8000 启动

## 📡 API 接口

### 健康检查

```http
GET /health
```

### 获取模型列表

```http
GET /v1/models
```

### 获取模型详情

```http
GET /v1/models/{model_name}/info
```

### URL 移除背景

```http
POST /v1/bg/remove/url
Content-Type: application/json

{
    "image_url": "https://example.com/image.jpg",
    "output_type": "file",      // "file" 或 "oss"
    "output_path": "output.png",
    "model": "isnet-anime",     // 可选: u2net, u2net_human_seg, isnet-anime, birefnet-portrait
    "stream": false             // 是否流式响应
}
```

### 文件上传移除背景

```http
POST /v1/bg/remove/file
Content-Type: multipart/form-data

file: <binary>
output_type: file
output_path: output.png
model: isnet-anime
stream: false
```

## 🎨 模型说明

| 模型名称 | 适用场景 | 文件大小 | 说明 |
|---------|---------|---------|------|
| `u2net` | 通用场景 | ~168MB | 默认模型，通用背景移除 |
| `u2net_human_seg` | 人像照片 | ~168MB | 专门针对人像分割优化 |
| `isnet-anime` | 动漫/卡通 | ~176MB | ⭐ **动漫/卡通人物专用模型** |
| `birefnet-portrait` | 高精度人像 | ~220MB | 高精度人像分割 |

### 模型选择建议

- **动漫/卡通人物**: 使用 `isnet-anime` 模型，效果最佳
- **人像照片**: 使用 `u2net_human_seg` 或 `birefnet-portrait`
- **通用场景**: 使用 `u2net`

## 🧪 测试脚本

### 综合测试

```bash
python examples/test_all.py
```

### 文件处理测试

```bash
# 单文件
python examples/test_file_single.py

# 批量文件
python examples/test_file_batch.py
```

### URL 处理测试

```bash
# 单 URL
python examples/test_url_single.py

# 批量 URL
python examples/test_url_batch.py
```

### 动漫模型测试

```bash
python examples/test_anime_model.py
```

## 📊 响应格式

### 非流式响应

```json
{
    "success": true,
    "data": {
        "url": "./output/output.png",
        "path": "output.png",
        "width": 512,
        "height": 512,
        "format": "PNG",
        "processing_time": 2.35
    }
}
```

### 流式响应 (NDJSON)

```
{"type": "start", "timestamp": 1700000000}
{"type": "progress", "step": "process", "percent": 30, "message": "正在移除背景..."}
{"type": "progress", "step": "output", "percent": 70, "message": "正在保存结果..."}
{"type": "complete", "result": {"url": "./output/output.png", ...}}
```

## 💻 客户端示例

### Python 客户端

```python
import httpx

async def remove_bg():
    async with httpx.AsyncClient() as client:
        # 使用动漫模型
        response = await client.post(
            "http://localhost:8000/v1/bg/remove/url",
            json={
                "image_url": "https://example.com/anime.jpg",
                "output_type": "file",
                "output_path": "output.png",
                "model": "isnet-anime",
                "stream": False
            }
        )
        result = response.json()
        print(result)
```

### cURL 示例

```bash
# 使用动漫模型移除背景
curl -X POST "http://localhost:8000/v1/bg/remove/file" \
  -F "file=@anime_image.jpg" \
  -F "model=isnet-anime" \
  -F "output_type=file" \
  -F "output_path=output.png"
```

## ⚙️ 配置说明

### 环境变量

| 变量名 | 默认值 | 说明 |
|-------|-------|------|
| `HOST` | 0.0.0.0 | 服务器监听地址 |
| `PORT` | 8000 | 服务器端口 |
| `OUTPUT_DIR` | ./output | 输出文件夹 |
| `MODEL_DIR` | ./models | 模型文件夹 |
| `DEFAULT_MODEL` | u2net | 默认模型 |
| `OSS_ACCESS_KEY_ID` | - | 阿里云 OSS Access Key |
| `OSS_ACCESS_KEY_SECRET` | - | 阿里云 OSS Secret |
| `OSS_BUCKET` | - | 阿里云 OSS Bucket |
| `OSS_ENDPOINT` | oss-cn-beijing.aliyuncs.com | 阿里云 OSS Endpoint |

## 📝 注意事项

1. **模型下载**: 首次使用某个模型时会自动下载（约 150-220MB），可以通过 `python download_models.py` 预下载
2. **GPU 支持**: rembg 自动检测并使用 GPU，无需额外配置
3. **内存占用**: 大图像处理可能占用较多内存，建议适当限制图像尺寸
4. **并发处理**: 批量处理时注意控制并发数，避免内存溢出

## 🔧 常见问题

### Q: 模型下载慢？
A: 模型文件较大（150-220MB），首次下载需要等待。可运行 `python download_models.py` 预下载。

### Q: 动漫图片效果不佳？
A: 请使用 `isnet-anime` 模型，这是专门为动漫/卡通人物优化的模型。

### Q: 如何添加自定义模型？
A: 将模型文件放入 `./models` 文件夹，并在 `bg_remover.py` 的 `MODELS` 列表中添加模型名称。

## 📄 许可证

MIT License

## 🙏 致谢

- [rembg](https://github.com/danielgatis/rembg) - 背景移除核心库
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
