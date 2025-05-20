# SmartImageFinder

一个基于多模态向量模型及视觉多模态模型构建的智能图片搜索引擎和管理系统，实现精准的以文搜图、以图搜图等多种智能检索方式，并提供完整的图片管理解决方案。本项目采用 FastAPI + React 技术栈，集成 Jina CLIP V2 和多模态大语言模型，为个人图片管理提供一站式解决方案。

## 功能特点

### 图片管理

- 直观的图片浏览界面，支持网格式布局和图片预览
- 强大的标签管理系统，支持多标签分类和过滤
- 灵活的元数据编辑功能，包括标题、描述和自定义标签
- 高效的批量操作支持，包括上传、分析和标签管理
- 支持拖放上传和多文件选择

### 多模态AI分析

- 基于 CLIP V2 模型的高精度向量编码
- 支持三种向量检索模式：
  - 文本-图片匹配：通过自然语言描述查找相似图片
  - 图片-图片匹配：基于参考图片查找相似内容
  - 混合向量搜索：结合标题、描述和图片内容的多维度搜索
- 集成多模态视觉模型API，提供智能图片分析：
  - 自动生成图片标题和详细描述
  - 智能提取关键标签
  - 支持批量AI分析处理

### 用户界面

- 基于 React + Ant Design 的现代化界面设计
- 响应式布局，适配不同屏幕尺寸
- 支持图片预览、放大和编辑操作
- 直观的标签筛选和搜索界面
- 实时显示处理进度和状态提示
- 支持深色/浅色主题切换

## 使用场景

- 个人图片库管理与组织
- 设计素材检索与管理
- 图片资源智能分类与检索
- 基于内容的图片相似度搜索
- 智能图片标注与描述生成

## 技术架构

### 后端

- FastAPI 框架提供高性能API服务
- SQLite + sqlite-vec 实现轻量化高效向量存储和检索
- Jina CLIP V2 模型用于特征向量提取
- 集成多模态大模型API进行内容理解和生成

### 前端

- React 18 + TypeScript 构建用户界面
- Ant Design 5.x 提供UI组件库
- Vite 作为开发和构建工具
- Axios 处理HTTP请求
- 支持文件拖放和批量处理

## 核心功能展示

- 多模态搜索：支持文本搜索、图像搜索和混合搜索
- 智能标签：自动生成和管理图片标签
- 元数据管理：灵活编辑和组织图片信息
- AI分析：智能生成图片描述和标签
- 批量处理：高效处理大量图片文件
- 系统管理：监控系统状态和配置管理

## 环境要求

- Python 3.8+
- Node.js 16+
- SQLite 3
- 支持CUDA的GPU（推荐但不是必需）
- 足够的磁盘空间用于存储图片和向量数据

## 快速开始

1. 克隆仓库:

```bash
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder
```

2. 安装依赖:

```bash
pip install -r requirements.txt
```

3. 配置系统:

```bash
# 复制默认配置
cp backend/config/config.example.yaml backend/config/config.yaml
# 根据需要编辑配置文件
```

---

```json
AVAILABLE_VISION_MODELS: # 可用的视觉模型列表,可以自己加，只要对应的厂商支持
- Qwen/Qwen2.5-VL-32B-Instruct
- Pro/Qwen/Qwen2.5-VL-7B-Instruct 
DB_PATH: ./data/db/smartimagefinder.db # 数据库路径
HOST: 0.0.0.0 # 这里不要动
PORT: 1000 # 后端的端口号
IMAGE_VECTOR_CACHE_DIR: ./data/caches/image_vector_cache
TEXT_VECTOR_CACHE_DIR: ./data/caches/text_vector_cache
MAX_CACHE_SIZE_GB: 1.5
MODEL_PATH: jinaai/jina-clip-v2 # 我推荐先下载模型到本地，然后将路径替换过来
EMBEDDING_DIMENSION: 1024
OPENAI_API_BASE: https://api.siliconflow.cn/v1 # 如果需要换成其他API服务商，请修改此处
OPENAI_API_KEY: # 填入你的OpenAI API密钥 
UPLOAD_DIR: ./data/images # 上传的图片存放目录
TEMP_DIR: ./data/temp # 临时文件存放目录
USE_CACHE: true # 是否使用缓存
VISION_MODEL: Qwen/Qwen2.5-VL-32B-Instruct # 当前使用的视觉模型的名称
# 添加向量数据库驱动的路径配置
VECTOR_DB_DRIVER: ./backend/config_files/vector_db_driver/vec0.dll # 向量数据库驱动的路径配置


```

注意⚠️： 默认的驱动是Windows电脑使用的，如果是mac或者linux电脑需要去<https://github.com/asg017/sqlite-vec/releases> 下载对应的驱动，并且把路径替换上来，如果你直接放到backend\config_files\vector_db_driver目录下面就可以直接换文件名即可，如果你直接换成绝对路径也可。
4. 启动后端服务:

```bash
python main.py
```

服务将在 `http://localhost:1000` 上运行，API文档可在 `http://localhost:1000/docs` 上查看。

### 前端设置

1. 进入前端目录:

```bash
cd frontend
```

2. 安装依赖:

```bash
npm install
```

3. 启动开发服务器:

```bash
npm run dev
```

前端将在 <http://localhost:5173> 上运行。

## 系统配置

### 前端配置

修改前端API请求地址在 `vite.config.ts` 文件中:[vite.config.ts](frontend/vite.config.ts)

### 后端配置

系统核心配置在 `backend/config_files/config.yaml` 配置文件中:
![backend_config](backend/config_files/config.yaml)
默认会加载系统配置文件，你也可以去掉从默认文件里面加载配置，然后使用[config.py](backend/config.py)里面的配置。

## 系统架构

![SmartImageFinder-项目架构图-v3.png](assets/images/SmartImageFinder-项目架构图-v3.png)

## 扩展开发

### 添加新功能

- 见 `docs/` 目录下的开发指南文档

### 自定义模型

- 系统支持自定义替换向量模型和视觉模型
- 修改 `config.yaml` 中的相关配置

## 文档

详细的系统文档:

- [系统配置指南](docs/config_guide.md)
- [数据库设计](docs/database_design.md)
- [系统设计指南](docs/design_guide.md)
- [API文档](docs/api_docs/main.md)

## 许可证

本项目采用 [Apache 许可证 2.0](LICENSE) 进行许可。
