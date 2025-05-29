<div align="center">
  <img src="assets/logo/logo.png" alt="SmartImageFinder Logo" width="200">
  <h1>SmartImageFinder</h1>

  <p>基于多模态向量模型和视觉多模态模型的智能图片搜索引擎和管理系统</p>

  <div>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
    <img src="https://img.shields.io/badge/version-1.0.0-green.svg" alt="Version">
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.100+-orange.svg" alt="FastAPI">
    <img src="https://img.shields.io/badge/React-18-61DAFB.svg" alt="React">
  </div>

  <div>
    <a href="README.md">中文</a> | 
    <a href="README_EN.md">English</a>
  </div>
</div>

## 项目概述

一个智能的图片搜索引擎和管理系统，能够实现精准的文本检图、以图搜图等智能检索方式，同时提供完整的图片管理解决方案。该项目采用 FastAPI + React 技术栈，集成 Jina CLIP V2 和多模态大语言模型，为个人图片管理提供一站式解决方案。

## 功能特性

### 图片管理

- 直观的图片浏览界面，支持网格布局和图片预览
- 强大的标签管理系统，支持多标签分类和筛选
- 灵活的元数据编辑，包括标题、描述和自定义标签
- 高效的批量操作支持，包括批量上传、分析和标签管理
- 支持拖拽上传和多文件选择

### 多模态AI分析

- 基于 CLIP V2 模型的高精度向量编码
- 支持三种向量检索模式：
  - 文本匹配图像：通过自然语言描述查找相似图片
  - 图像匹配图像：基于参考图片查找相似内容
  - 混合向量搜索：结合标题、描述和图片内容的多维度搜索
- 集成多模态视觉模型API，实现智能图片分析：
  - 自动生成图片标题和详细描述
  - 智能提取关键标签
  - 支持批量AI分析处理

### 用户界面

- 基于 React + Ant Design 的现代化界面设计
- 响应式布局，适配不同屏幕尺寸
- 支持图片预览、缩放和编辑操作
- 直观的标签筛选和搜索界面
- 实时显示处理进度和状态通知
- 支持深色/浅色主题切换

## 应用场景

- 个人图片库管理和整理
- 设计素材检索和管理
- 智能图片分类和检索
- 基于内容的图片相似性搜索
- 智能图片标注和描述生成

## 技术架构

### 后端

- FastAPI 框架提供高性能API服务
- SQLite + sqlite-vec 实现轻量级高效的向量存储和检索
- Jina CLIP V2 模型进行特征向量提取
- 集成多模态大模型API进行内容理解和生成

### 前端

- React 18 + TypeScript 构建用户界面
- Ant Design 5.x 提供UI组件库
- Vite 作为开发和构建工具
- Axios 处理HTTP请求
- 支持文件拖拽和批量处理

## 核心功能展示

- 多模态搜索：支持文本搜索、图片搜索和混合搜索
- 智能标签：自动生成和管理图片标签
- 元数据管理：灵活编辑和组织图片信息
- AI分析：智能生成图片描述和标签
- 批量处理：高效处理大量图片文件
- 系统管理：监控系统状态和配置管理

## 系统要求

- Python 3.8+
- Node.js 16+
- SQLite 3
- 支持CUDA的GPU（推荐但不是必需）
- 足够的磁盘空间用于存储图片和向量数据

## 快速开始

1. 克隆仓库：

```bash
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置系统：

```bash
# 复制默认配置
cp backend/config/config.example.yaml backend/config/config.yaml
# 根据需要编辑配置文件
```

---

```yaml
AVAILABLE_VISION_MODELS: # 可用的视觉模型列表，你可以自己添加，只要对应的厂商支持就行
- Qwen/Qwen2.5-VL-32B-Instruct
- Pro/Qwen/Qwen2.5-VL-7B-Instruct 
DB_PATH: ./data/db/smartimagefinder.db # 数据库路径
HOST: 0.0.0.0 # 不要修改这个
PORT: 1000 # 后端端口号
IMAGE_VECTOR_CACHE_DIR: ./data/caches/image_vector_cache
TEXT_VECTOR_CACHE_DIR: ./data/caches/text_vector_cache
MAX_CACHE_SIZE_GB: 1.5
MODEL_PATH: jinaai/jina-clip-v2 # 我建议先把模型下载到本地，然后把路径替换这里
EMBEDDING_DIMENSION: 1024
OPENAI_API_BASE: https://api.siliconflow.cn/v1 # 如果你需要切换到其他API提供商，修改这里
OPENAI_API_KEY: # 填入你的OpenAI API密钥
UPLOAD_DIR: ./data/images # 上传图片的目录
TEMP_DIR: ./data/temp # 临时文件目录
USE_CACHE: true # 是否使用缓存
VISION_MODEL: Qwen/Qwen2.5-VL-32B-Instruct # 当前使用的视觉模型名称
# 添加向量数据库驱动路径配置
VECTOR_DB_DRIVER: ./backend/config_files/vector_db_driver/vec0.dll # 向量数据库驱动的路径配置
```

注意⚠️：默认驱动是Windows电脑的，如果你是Mac或Linux电脑，需要从<https://github.com/asg017/sqlite-vec/releases>下载对应的驱动并替换路径。如果你直接放在backend\config_files\vector_db_driver目录下，只需要改文件名即可。你也可以使用绝对路径。

4. 启动后端服务：

```bash
python main.py
```

服务将运行在 `http://localhost:1000`，API文档可在 `http://localhost:1000/docs` 查看。

### 前端设置

1. 进入前端目录：

```bash
cd frontend
```

2. 安装依赖：

```bash
npm install
```

3. 启动开发服务器：

```bash
npm run dev
```

前端将运行在 <http://localhost:5173>。

## 系统配置

### 前端配置

在 `vite.config.ts` 文件中修改前端API请求地址：[vite.config.ts](frontend/vite.config.ts)

### 后端配置

系统核心配置在 `backend/config_files/config.yaml` 配置文件中：
![backend_config](backend/config_files/config.yaml)
默认情况下会加载系统配置文件，你也可以移除默认文件的配置加载，使用[config.py](backend/config.py)中的配置。

## 演示截图

### 系统架构

![系统架构](assets/images/SmartImageFinder-项目架构图-v3.png)

### 首页展示

![首页](assets/images/首页.png)
![首页图片侧边栏展示](assets/images/首页图片侧边栏展示.png)

### 图片上传和分析

![图片上传](assets/images/图片上传.png)
![上传时可编辑图片分析内容](assets/images/上传的时候可以编辑图片分析内容.png)
![上传完成结果显示](assets/images/上传完成的结果显示.png)
![AI自动分析图片内容](assets/images/AI自动分析图片内容.png)
![AI自动分析图片内容效果](assets/images/AI自动分析图片内容效果.png)

### 标签管理系统

![标签管理](assets/images/标签管理.png)
![标签编辑](assets/images/标签编辑.png)
![标签编辑效果](assets/images/标签编辑效果.png)
![标签搜索及过滤](assets/images/标签搜索及过滤.png)
![点击标签可以直接跳转到对应的图片展示部分并过滤图片](assets/images/点击标签可以直接跳转到对应的图片展示部分并过滤图片.png)
![基于标签的过滤搜索](assets/images/基于标签的过滤搜索.png)

### 智能搜索功能

![基于模糊搜索的图片搜索](assets/images/基于模糊搜索的图片搜索.png)
![标题向量搜索](assets/images/标题向量搜索.png)
![标题向量和描述向量混合搜索](assets/images/标题向量和描述向量混合搜索.png)
![三种混合搜索的搜索效果](assets/images/三种混合搜索的搜索效果.png)
![使用图搜索图](assets/images/使用图搜索图.png)

### 元数据管理

![元数据编辑](assets/images/元数据编辑.png)
![元数据编辑效果](assets/images/元数据编辑效果.png)
![图片描述更新](assets/images/图片描述更新.png)

### 系统管理

![系统设置](assets/images/系统设置.png)
![系统状态查看](assets/images/系统状态查看.png)

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

## 联系方式

如果您在使用过程中遇到任何问题或有任何建议，欢迎联系我：

<div align="center">
  <img src="assets/wechat/筱可AI研习社_258.jpg" alt="筱可AI研习社" width="200">
  <p>扫描二维码关注"筱可AI研习社"公众号</p>
</div>