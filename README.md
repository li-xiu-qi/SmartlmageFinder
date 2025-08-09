<div align="center">
  <img src="assets/logo/logo.png" alt="SmartImageFinder Logo" width="200">
  <h1>SmartImageFinder</h1>

  <p>智能图片搜索 / 管理与 AI 对话式推荐系统</p>

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

SmartImageFinder 是一个现代化的智能图片搜索引擎和管理系统，采用双层微服务架构设计，提供高性能的图片管理和智能检索功能。系统集成了先进的向量搜索技术和AI分析能力，为用户提供一站式图片管理解决方案。

## 🏗️ 系统架构

### 架构概览

当前版本采用轻量一体化后端（FastAPI）+ 前端（React）架构，AI 推荐 / 对话代理集成在 `backend/ai_func/recommendation` 中，结合 sqlite-vec 向量检索与 SSE 流式输出，无需额外独立 AI 微服务即可完成智能搜索与多轮推荐。

## 功能特性

### 🖼️ 图片管理

- **图片浏览** - 直观的网格布局和图片预览功能
- **标签系统** - 强大的多标签分类和筛选管理
- **元数据编辑** - 灵活的标题、描述和自定义标签管理
- **批量操作** - 高效的批量上传、分析和标签管理
- **拖拽上传** - 支持多文件选择和拖拽上传

### 🔍 智能搜索

- **文本搜索** - 基于自然语言描述的图片检索
- **图片搜索** - 以图搜图，查找相似内容
- **向量搜索** - 基于标题、描述和图片内容的多维度搜索
- **相似搜索** - 基于参考图片的相似性检索
- **过滤搜索** - 支持标签和时间的组合过滤

### 🤖 AI分析功能

- **自动分析** - 基于CLIP模型的图片内容理解
- **智能标注** - 自动生成图片标题、描述和标签
- **批量处理** - 支持大规模图片的批量AI分析
- **API集成** - 支持多种多模态视觉模型API

### 🎨 用户界面

- **现代化设计** - 基于React 18 + Ant Design 5的精美界面
- **响应式布局** - 完美适配桌面端和移动端
- **实时交互** - 支持图片预览、缩放和编辑操作
- **状态监控** - 实时显示处理进度和系统状态
- **系统管理** - 完善的配置管理和监控界面

## 🎯 核心技术特点

- **🧠 对话式推荐代理** - 支持多轮上下文（64K滚动窗口）+ 工具函数调用
- **🛡️ 向量目标白名单** - 防止非法表名/注入导致的表不存在错误
- **🔌 流式SSE输出** - AI 推荐过程逐步推送（改写、搜索、结果）提升交互体验
- **⚡ 高性能向量检索** - SQLite + sqlite-vec 轻量级向量数据库，毫秒级搜索响应
- **🧠 先进的AI模型** - 集成Jina CLIP V2模型，提供精准的多模态搜索能力
- **🎨 现代化技术栈** - React 18 + TypeScript + FastAPI，确保代码质量和开发体验
- **🔧 智能启动管理** - 一键启动脚本，自动处理环境配置和依赖管理


## 🚀 快速开始

### 环境初始化

首次使用需要初始化环境：

```bash
# 克隆项目
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder

# 环境初始化（自动安装依赖、下载模型、生成配置）
python start.py init
```

### 启动服务

```bash
# 启动主服务（前后端）
python start.py

# 仅启动后端服务
python start.py --backend-only

# 仅启动前端服务
python start.py --frontend-only
```

启动脚本会自动：
✅ 检查环境依赖  ✅ 安装所需包  ✅ 下载AI模型  ✅ 启动服务

## 应用场景

- **个人图片管理** - 智能整理和检索个人照片库
- **设计素材管理** - 高效管理和搜索设计资源
- **内容创作** - 为创作者提供智能图片检索服务
- **企业资产管理** - 企业级的图片资源管理解决方案
- **AI研究应用** - 多模态AI技术的研究和应用平台

## 🛠️ 技术架构

### 主服务技术栈

#### 后端 (`backend/`)

- **FastAPI** - 高性能异步Web框架
- **SQLite + sqlite-vec** - 轻量级向量数据库
- **Jina CLIP V2** - 多模态向量编码模型
- **连接池管理** - 高效的数据库连接管理
- **向量缓存** - diskcache实现的向量缓存系统

#### 前端 (`frontend/`)

- **React 18 + TypeScript** - 现代化前端框架
- **Ant Design 5.25** - 企业级UI组件库
- **Vite** - 快速构建工具
- **React Router 7.5** - 路由管理
- **Axios** - HTTP客户端

### AI服务技术栈

#### AI后端 (`ai_backend/`)

- **FastAPI** - AI服务API框架
- **推荐算法** - 智能图片推荐引擎
- **多模态分析** - 图片内容理解和分析

#### AI前端 (`ai_frontend/`)

- **React 18 + TypeScript** - AI交互界面
- **Ant Design 5.4** - UI组件库
- **智能搜索** - AI驱动的搜索体验

### 核心组件

- **向量搜索引擎** - 支持多种搜索模式（文本、图片、向量、相似）
- **AI分析引擎** - 自动图片内容分析和标注
- **标签管理系统** - 智能标签分类和管理
- **缓存系统** - 高性能向量缓存机制
- **配置管理** - 灵活的系统配置管理

## 🖥️ 系统要求

### 支持平台

- **Windows**: x86_64
- **Linux**: x86_64, aarch64  
- **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)

### 软件要求

- **Python**: 3.8+
- **Node.js**: 16+
- **内存**: 推荐 4GB+
- **存储**: 足够空间存储图片和向量数据
- **网络**: 首次启动需要下载AI模型

## 📁 项目结构

```
SmartImageFinder/
├── backend/                 # 主后端服务
│   ├── routers/            # API路由模块
│   ├── db_func/           # 数据库操作
│   ├── ai_func/           # AI分析功能
│   └── config_files/      # 配置文件
├── frontend/               # 主前端服务
│   ├── src/pages/         # 页面组件
│   ├── src/components/    # 通用组件
│   └── src/services/      # API服务层
├── backend/ai_func/recommendation/  # 对话式推荐与工具调用逻辑
├── models/                # AI模型文件
├── data/                  # 数据存储
│   ├── db/               # 数据库文件
│   ├── images/           # 图片存储
│   └── caches/           # 向量缓存
├── scripts/               # 启动和管理脚本
├── requirements.txt       # Python依赖
└── start.py              # 启动入口
```

## 🔧 详细配置

### 服务端口

- **后端**: 10050 (从 config.yaml 读取)
- **前端**: 5173 (Vite 默认)

### 配置文件

主要配置文件位于 `backend/config_files/config.yaml`：

```yaml
MODEL_PATH: ./models/yizhixiaoke/xiaoke-jina-clip-v2  # 模型路径
VECTOR_DB_DRIVER_DIR: ./backend/config_files/vector_db_driver  # 向量数据库驱动
UPLOAD_DIR: ./data/images  # 图片上传目录
DB_PATH: ./data/db/smartimagefinder.db  # 数据库路径
HOST: 0.0.0.0  # 服务监听地址
PORT: 10050  # 服务端口
```

### 环境变量

支持通过环境变量覆盖配置：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.openai.com/v1"
```

### 💡 使用提示

#### 服务访问地址

- **主前端界面**: <http://localhost:5173>
- **主后端API**: <http://localhost:10050>  
- **API文档**: <http://localhost:10050/docs>
- **AI前端**: 需要单独启动AI服务后访问

## 📊 系统监控与管理

### 系统状态监控

通过系统设置页面可以实时监控：

- **系统信息** - CPU、内存、磁盘使用情况
- **数据库状态** - 连接池状态、表统计信息
- **存储信息** - 图片数量、标签数量、存储使用情况
- **缓存状态** - 缓存使用情况
- **向量数据库** - 驱动状态、索引信息


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
