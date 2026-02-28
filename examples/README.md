# 测试脚本说明

这个目录包含各种测试脚本，用于测试背景移除服务的不同功能。

## 脚本列表

### 1. 综合测试
- **test_all.py** - 运行所有测试，检查服务状态和功能

```bash
python examples/test_all.py
```

### 2. 文件进文件出

#### 单条处理
- **test_file_single.py** - 单文件处理测试

```bash
# 修改脚本中的配置
INPUT_FILE = "test_input.png"    # 输入文件路径
OUTPUT_FILE = "test_output.png"  # 输出文件路径
MODEL = "isnet-anime"            # 模型选择

# 运行
python examples/test_file_single.py
```

#### 批量处理
- **test_file_batch.py** - 批量文件处理测试

```bash
# 修改脚本中的配置
INPUT_DIR = "./test_images"      # 输入文件夹
OUTPUT_DIR = "./test_output"     # 输出文件夹
MODEL = "isnet-anime"            # 模型选择
CONCURRENT_LIMIT = 3             # 并发数

# 运行
python examples/test_file_batch.py
```

### 3. URL进URL出

#### 单条处理
- **test_url_single.py** - 单URL处理测试

```bash
# 修改脚本中的配置
TEST_IMAGE_URL = "https://example.com/image.jpg"
OUTPUT_PATH = "url_output.png"
MODEL = "u2net_human_seg"

# 运行
python examples/test_url_single.py
```

#### 批量处理
- **test_url_batch.py** - 批量URL处理测试

```bash
# 修改脚本中的URL列表
TEST_URLS = [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
]

# 运行
python examples/test_url_batch.py
```

### 4. 动漫专用模型测试
- **test_anime_model.py** - 动漫/卡通人物专用模型测试

```bash
# 1. 准备动漫图片到 ./test_anime/ 目录
# 2. 运行测试
python examples/test_anime_model.py
```

## 可用模型

| 模型名称 | 适用场景 | 说明 |
|---------|---------|------|
| `u2net` | 通用场景 | 默认模型 |
| `u2net_human_seg` | 人像照片 | 人像分割专用 |
| `isnet-anime` | 动漫/卡通 | ⭐ **动漫人物专用** |
| `birefnet-portrait` | 高精度人像 | 高质量人像分割 |

## 快速开始

### 1. 启动服务

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m src.bg_remover.main
```

### 2. 运行综合测试

```bash
python examples/test_all.py
```

### 3. 测试动漫图片

```bash
# 准备动漫图片
mkdir -p test_anime
cp your_anime_image.png test_anime/

# 运行动漫模型测试
python examples/test_anime_model.py
```

## 测试文件准备

### 文件测试
```bash
# 创建测试目录
mkdir -p test_images
mkdir -p test_anime
mkdir -p test_output

# 放入测试图片
cp your_image.png test_input.png
cp anime1.png test_anime/
cp anime2.png test_anime/
```

### URL测试
修改脚本中的 `TEST_URLS` 列表，替换为实际的图片URL。

## API 端点

### 健康检查
```
GET /health
```

### 获取模型列表
```
GET /v1/models
```

### 获取模型详情
```
GET /v1/models/{model_name}/info
```

### 文件处理
```
POST /v1/bg/remove/file
Content-Type: multipart/form-data

file: <图片文件>
model: isnet-anime
output_type: file
output_path: output.png
stream: false
```

### URL处理
```
POST /v1/bg/remove/url
Content-Type: application/json

{
    "image_url": "https://example.com/image.jpg",
    "model": "isnet-anime",
    "output_type": "file",
    "output_path": "output.png",
    "stream": false
}
```

## 注意事项

1. **确保服务已启动** - 测试前需要先启动背景移除服务
2. **准备测试图片** - 文件测试需要准备测试图片
3. **配置URL** - URL测试需要配置可访问的图片URL
4. **模型下载** - 首次使用某个模型时会自动下载（约150-220MB）

## 常见问题

### Q: 测试提示文件不存在？
A: 请确保测试图片已放入正确位置，或修改脚本中的路径配置。

### Q: URL测试失败？
A: 请确保URL可访问，且服务有网络访问权限。

### Q: 模型下载慢？
A: 模型文件较大（150-220MB），首次下载需要等待。可运行 `python download_models.py` 预下载。

### Q: 动漫图片效果不佳？
A: 请使用 `isnet-anime` 模型，这是专门为动漫/卡通人物优化的模型。
