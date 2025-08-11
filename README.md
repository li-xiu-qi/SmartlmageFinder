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

SmartImageFinder 是一个现代化的智能图片搜索与管理系统，采用轻量一体化 FastAPI 后端 + React 前端架构，集成向量语义检索、以图搜图、模糊检索与对话式 AI 推荐。当前默认内置多模态/文本统一向量模型已升级为 Jina Embeddings v4（替代原 Jina CLIP V2），提供更高质量的语义表示。

## 🏗️ 系统架构

### 架构概览

![系统架构](docs/架构图.png)
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
- **模糊搜索 (Fuzzy LIKE)** - 轻量关键词 LIKE 匹配，适合快速匹配式搜索

#### 💬 对话式图片搜索（Chat-driven Image Retrieval）

基于对话的多轮图片智能检索与推荐：

- **多轮上下文记忆**：支持 64K 滚动窗口对话历史，自动裁剪保留关键信息
- **智能查询改写**：对用户输入进行归一化/关键词抽取，提升向量检索命中率
- **分阶段流程**：改写 -> 多向量检索（标题/描述/图像内容）-> 结果重排序 -> 生成回复
- **SSE 流式输出**：事件包括 `rewrite_start` / `assistant_delta` / `complete` / `error`
- **会话管理**：支持创建 / 列出 / 删除会话，`conversation_id` 绑定上下文
- **结果增强**：返回图片精简信息（id/score/title/tags/public_url）+ 选中图片ID列表

主要接口：

| 功能 | 方法 | 路径 |
|------|------|------|
| 创建会话 | POST | `/api/v1/ai/conversations/create` |
| 列出会话 | GET  | `/api/v1/ai/conversations` |
| 删除会话 | DELETE | `/api/v1/ai/conversations/{conversation_id}` |
| 获取会话消息 | GET | `/api/v1/ai/conversations/{conversation_id}/messages` |
| 对话式推荐（一次性） | POST | `/api/v1/ai/recommend/chat` |
| 对话式推荐（SSE流） | POST | `/api/v1/ai/recommend/chat/stream` |

请求示例（流式推荐，端口以启动日志为准；也可通过环境变量 SIF_PORT 或根目录 start_config.yaml 配置）：

```bash
# 注意：将 8000 替换为你实际启动时显示的后端端口（或通过 SIF_PORT 指定）
curl -N -X POST http://localhost:8000/api/v1/ai/recommend/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "demo-session-1",
    "query": "给我找一些蓝色天空下的城市建筑照片",
    "vector_targets": ["title_vector", "desc_vector", "image_vector"],
    "limit": 12
  }'
```

SSE 返回关键事件（示例）：

```text
event: rewrite_start
data: {"message":"start","conversation_id":"demo-session-1"}

event: assistant_delta
data: {"delta":"正在为你检索相关图片..."}

event: complete
data: {"image_ids":[12,8,5,...],"assistant_text":"已为你找到...","images_brief":[...]} 
```

前端可基于事件类型实时渲染“AI思考中 / 追加回答 / 展示图片结果”等状态，带来顺滑的交互体验。

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
- **🧠 先进的AI模型** - 集成 Jina Embeddings v4 模型（支持文本/图片多模态向量），相比旧版 Jina CLIP V2 召回与语义表示更优
- **🎨 现代化技术栈** - React 18 + TypeScript + FastAPI，确保代码质量和开发体验
- **🔧 智能启动管理** - 一键启动脚本，自动处理环境配置和依赖管理
- **🔄 离线向量模型迁移** - 提供可断点续传的离线脚本 `migrate_embeddings.py`，支持自动探测维度 / 新旧维度差异判定 / 原子切换 `*_vectors` 虚表 / 缓存目录安全替换，并在完成后自动更新主配置的 `MODEL_PATH` 与 `EMBEDDING_DIMENSION`。

### 🔄 向量模型迁移（Embedding Model Migration）

当你需要将当前使用的向量模型（例如从 Jina CLIP V2 升级为 Jina Embeddings v4，或切换到任意其他本地 / HuggingFace 模型）并重新生成图片 / 标题 / 描述三类向量时，可使用根目录脚本：

```bash
python migrate_embeddings.py            # 使用默认配置文件 backend/config/files/migration.yaml
python migrate_embeddings.py --resume   # 中断后续传
```

关键特性：

- 自动判定是否需要创建 `*_vectors_new`（维度变更才建新表，完成后原子切换）
- 分批处理 + `model_migrations` 表记录进度，可断点续传
- 避免 UPSERT 不支持：使用 INSERT OR IGNORE + UPDATE 兼容写入 sqlite-vec 虚表
- 成功后自动更新 `backend/config/files/config.yaml` 中模型路径与新维度
- 旧缓存目录自动重命名为 `*_old`，便于回滚 / 清理

运行前务必：停止后端服务并备份数据库文件（详见 `docs/model_migration.md`）。

更多细节、配置字段与回滚策略参见：`docs/model_migration.md`。

## 🚀 快速开始

### 环境初始化（推荐手动安装依赖，模型下载建议使用脚本）

> 安装依赖和下载模型可能耗时较长，建议首次分步手动操作。

```bash
# 克隆项目
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder

# 手动安装 Python 依赖
pip install -r requirements.txt

# 安装 Node.js 依赖（前端）
cd frontend
npm install
cd ..
```

> ⚠️ AI 模型下载建议使用 `python start.py init`，否则需自行下载并放置到 `models/` 目录。模型下载过程较慢，建议提前准备。

详细模型下载方式请参考 docs/model_migration.md 或 README 相关章节。

> 💡 完成首次环境初始化和模型下载后，后续启动项目可直接使用 `python start.py` 一键启动前后端服务，无需重复初始化。

### 启动服务

#### 方式一：使用 start.py 一键启动（自动安装依赖、下载模型、生成配置）

```bash
python start.py init
python start.py
```

#### 方式二：手动启动后端（推荐）

```bash
python main.py
```

#### 方式三：手动启动前端

```bash
cd frontend
npm run dev
```

> 推荐手动安装依赖和模型，避免脚本自动安装时等待过久。

### 端口与代理配置（重要）

- 后端启动参数优先级：CLI > 环境变量 > 默认值。
  - 支持 CLI：`python main.py --host 0.0.0.0 --port 8000 --reload`
  - 环境变量：
    - `SIF_HOST`（默认 `0.0.0.0`）
    - `SIF_PORT`（默认 `8000`）
    - `SIF_RELOAD`（`1/true` 启用热重载）
- 前端开发服务器端口：
  - `SIF_FRONTEND_PORT`（默认 `5173`），由 `frontend/vite.config.ts` 读取
  - 前端到后端代理目标：`SIF_BACKEND_ORIGIN`（未设置则自动拼接为 `http://{SIF_HOST}:{SIF_PORT}`）
- 一键启动脚本 `start.py` 会读取项目根目录可选文件 `start_config.yaml` 并设置上述环境变量，示例：

```yaml
# start_config.yaml 示例
backend_host: 0.0.0.0
backend_port: 10060
reload: true
frontend_port: 5176
# 可选：显式指定前端代理到的后端地址
backend_origin: http://localhost:10060
```



## 应用场景

- **个人图片管理** - 智能整理和检索个人照片库
- **设计素材管理** - 高效管理和搜索设计资源
- **内容创作** - 为创作者提供智能图片检索服务

## 🛠️ 技术架构

### 主服务技术栈

#### 后端 (`backend/`)

- **FastAPI** - 高性能异步Web框架
- **SQLite + sqlite-vec** - 轻量级向量数据库
- **Jina Embeddings v4** - 新一代多模态/文本统一向量编码模型（默认 2048 维）
- **连接池管理** - 高效的数据库连接管理
- **向量缓存** - diskcache实现的向量缓存系统
- **大模型智能重排** - 智能图片推荐
- **多模态分析** - 图片内容理解和分析

#### 前端 (`frontend/`)

- **React 18 + TypeScript** - 现代化前端框架
- **Ant Design 5.25** - 企业级UI组件库
- **Vite** - 快速构建工具
- **React Router 7.5** - 路由管理
- **Axios** - HTTP客户端

### 核心组件

- **向量搜索引擎** - 统一向量语义搜索（文本 / 图片 / 直接向量 / 相似）
- **AI分析引擎** - 自动图片内容分析和标注
- **标签管理系统** - 智能标签分类和管理
- **缓存系统** - 高性能向量缓存机制
- **配置管理** - 灵活的系统配置管理

## 🖥️ 系统要求

### 支持平台

- **Windows**: x86_64
- **Linux**: x86_64, aarch64  
- **macOS**: x86_64 (Intel), aarch64 (Apple Silicon)

## 📁 项目结构

```
SmartImageFinder/
├── backend/                       # 后端主服务（API、数据库、AI推荐等）
│   ├── routers/                   # 路由模块（images/tags/search/metadata等）
│   ├── db_func/                   # 数据库与向量相关操作
│   ├── ai_func/                   # AI分析与推荐（含 recommendation/agent.py）
│   ├── config/                    # 配置文件与驱动
│   └── global_schemas.py          # 通用响应模型
├── frontend/                      # 前端主服务（React+AntD）
│   ├── src/pages/                 # 页面组件
│   ├── src/components/            # 通用组件
│   ├── src/services/              # API服务层
│   └── public/                    # 静态资源
├── models/                        # AI模型文件（本地或下载）
├── data/                          # 数据存储
│   ├── db/                        # SQLite数据库文件
│   ├── images/                    # 图片存储
│   ├── caches/                    # 向量缓存
│   └── temp/                      # 临时文件
├── scripts/                       # 启动与环境管理脚本
├── docs/                          # 架构图与API文档
├── requirements.txt               # Python依赖
├── main.py                        # 后端主入口（API服务主文件）
├── start.py                       # 一键启动入口
└── README.md                      # 项目说明
```

## 🔧 详细配置

### 服务端口

- **后端**: 10050 (默认，可配置)
- **前端**: 5173 (Vite 默认)

### 配置文件

主要配置文件位于 `backend/config/files/config.yaml`：

```yaml
MODEL_PATH: ./models/jina-embeddings-v4  # 新模型路径 (原: ./models/yizhixiaoke/xiaoke-jina-clip-v2)
VECTOR_DB_DRIVER_DIR: ./backend/config/files/vector_db_driver  # 向量数据库驱动目录
EMBEDDING_DIMENSION: 2048  # 向量维度（与原模型保持兼容）
UPLOAD_DIR: ./data/images  # 图片上传目录
DB_PATH: ./data/db/smartimagefinder.db  # 数据库路径
HOST: 0.0.0.0  # 服务监听地址
PORT: 10050  # 服务端口（默认）
```

### 💡 使用提示

#### 服务访问地址

- **主前端界面**: <http://localhost:5173>
- **主后端API**: <http://localhost:10050>  
- **API文档**: <http://localhost:10050/docs>

## 📊 系统监控与管理

### 系统状态监控

通过系统设置页面可以实时监控：

- **系统信息** - CPU、内存、磁盘使用情况
- **数据库状态** - 连接池状态、表统计信息
- **存储信息** - 图片数量、标签数量、存储使用情况
- **缓存状态** - 缓存目录大小（已简化，不再显示条目数）
- **向量数据库** - 驱动状态、索引信息

### 缓存统计说明

缓存接口 `/api/v1/system/cache` 现在仅返回目录大小 (MB)、可选 cache.db 文件大小与 last_scan；清理后前端轮询 `/api/v1/system/cache/brief` 快速确认已归零。

### 对话式推荐 SSE 事件

流式端点只发送事件：`rewrite_start`、`assistant_delta`（多次）、`complete`、`error`；内部 selection 已聚合在 complete。

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 许可证。

## 联系方式

如果您在使用过程中遇到任何问题或有任何建议，欢迎联系我：

<div align="center">
  <img src="assets/wechat/筱可AI研习社_258.jpg" alt="筱可AI研习社" width="200">
  <p>扫描二维码关注"筱可AI研习社"公众号</p>
</div>
