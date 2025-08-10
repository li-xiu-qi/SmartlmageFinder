# SmartImageFinder 项目设计指南

## 项目概述

SmartImageFinder 是一个基于 Jina CLIP V2 模型的个人智能图片管理与检索系统。该系统集成 FastAPI、SQLite（含 sqlite-vec 向量搜索扩展）和 React + Ant Design 前端框架，并结合多模态模型 API（如硅基流动），提供全面的图片智能管理解决方案。

**核心定位**：本系统专为个人本地桌面Web应用场景设计，优先保障功能完整性与用户易用性，而非追求极致的性能扩展或复杂的网络优化。当前默认 FastAPI 服务端口为 8000（可在 config.yaml 中修改）。

### 核心功能

**通用特性**：所有检索模式均支持基于图片上传时间的范围查询过滤。此外，系统提供基于标签的分类管理和元数据管理功能。

系统支持以下主要功能模块：

#### 1. 检索模式

系统实际提供以下检索功能（基于现有路由实现）：

##### a. 标签检索
- **实现**：通过 `/api/v1/tags/by-tag/{tag}` 和 `/api/v1/tags/by-multiple-tags` 端点
- **机制**：基于标签的精确匹配和组合筛选
- **支持**：单标签查询、多标签OR/AND模式查询

##### b. 向量检索模式

- **统一语义检索**：`/api/v1/search/unified` 固定使用多向量语义检索（`search_type=vector`），可通过 `vector_targets[]` 指定 `title/description/image`
- **以图搜图**：`/api/v1/search/unified/image` 上传图片后进行图片向量相似检索
- **直接向量检索**：`/api/v1/search/unified/vector` 传入 embedding 数组直接检索
- **相似图片检索**：`/api/v1/search/similar/{image_id}` 基于已存在图片的向量做相似检索
- **技术实现**：
  - 基于 `sqlite-vec` 与 Jina CLIP V2 模型（维度以实际模型加载结果为准）
  - 三张向量表：`title_vectors`、`description_vectors`、`image_vectors` 与 `images` 通过 `image_id` 关联
- **安全约束**：向量目标白名单校验，拒绝非法表名注入

#### 2. 图片管理

- **实现**：通过FastAPI路由 `/api/v1/images/` 提供RESTful API
- **核心端点**：
  - `GET /`：获取图片列表（支持分页和排序）
  - `GET /{image_id}`：获取单个图片详情
  - `POST /upload`：上传图片
  - `PATCH /{image_id}`：更新图片信息
  - `DELETE /{image_id}`：删除单个图片
  - `DELETE /batch`：批量删除图片
- **数据存储**：
  - 图片文件存储在配置的 `UPLOAD_DIR` 目录
  - 元数据（标题、描述、标签）存储在SQLite的 `images` 表
  - 支持通过 `/api/v1/metadata/{image_id}/update` 更新元数据
- **实际功能**：基于标签的筛选、图片信息的CRUD操作“以图搜图”可直接以当前图片为基础进行相似图片搜索。
- **交互式标签筛选**：
  - 页面展示所有可用标签，点击标签可“点亮”并筛选包含该标签的图片。
  - 支持多标签选择以实现组合筛选。
  - 显示各标签对应的图片数量统计。
  - 提供标签快速取消和全部清除选项。
  - 标签筛选可与时间等其他检索条件组合使用。
- **图片加载策略**：
  - 利用 Ant Design 的 `Image` 组件实现懒加载和渐进式加载。
  - 图片浏览采用虚拟滚动技术，优化大量图片浏览时的流畅性。
  - **优化说明**：针对本地使用场景，无需生成和管理缩略图，优先保证功能实现。

#### 3. 图片上传与处理

- **上传实现**：通过 `/api/v1/images/upload` 端点实现
- **实际存储**：
  - 图片文件直接存储在配置的 `UPLOAD_DIR` 目录
  - 使用UUID作为文件名，保留原始文件名作为元数据
- **AI分析**：
  - 通过 `/api/v1/ai/analyze-upload-image` 端点实现图片分析
  - 通过 `/api/v1/ai/analyze-image-id/{image_id}` 端点实现已有图片分析
  - 自动生成标题、描述和标签（基于多模态AI模型）
- **实际数据流程**：
  1. 图片文件保存至文件系统
  2. 记录基础信息到SQLite `images` 表
  3. 计算并存储向量到三个向量表
  4. 可选：调用AI分析生成元数据并更新记录
- **元数据更新**：通过 `/api/v1/metadata/{image_id}/update` 端点实现

#### 4. 系统管理与配置

- **状态监控**：通过 `/api/v1/system/` 系列端点实现
  - `/info`：获取系统基本信息
  - `/runtime`：获取运行时状态
  - `/database`：数据库连接和状态信息
  - `/storage`：存储使用情况
  - `/cache`：缓存状态查看
  - `/cache/clear`：清理缓存（文本和图像向量缓存）
- **配置管理**：
  - 通过 `/api/v1/system/config` 和 `/config/update` 端点管理
  - 支持动态更新配置（OPENAI_API_KEY、存储路径、缓存大小等）
  - 配置验证使用Pydantic确保数据完整性
- **多端数据库驱动适配**：
  - 系统内置 `backend.db_func.platform_detector` 模块
  - 支持 Windows/Linux/macOS 的 x86_64 和 aarch64 架构
  - 自动从 `VECTOR_DB_DRIVER_DIR` 选择匹配的 sqlite-vec 驱动文件
  - 驱动文件包含在 `backend/config_files/vector_db_driver/` 目录中

#### 5. 图片存储与文件管理

- **实际存储结构**：
  - 图片文件存储在配置的 `UPLOAD_DIR` 目录（默认为 `./data/images`）
  - 使用UUID作为唯一文件名：`{uuid}.jpg` 等格式
  - 原始文件名保存在 `images.filename` 字段中
- **文件访问**：
  - 通过FastAPI静态文件服务直接访问本地文件
  - 无需网络传输优化，适合本地使用场景
- **元数据关联**：
  - SQLite `images` 表中的 `filepath` 字段存储完整文件路径
  - 其他关联数据：
    - 向量数据：通过 `image_id` 关联到三个向量表
    - 标签数据：通过 `tags` 字段（JSON数组格式）
    - 元数据：通过 `metadata` 字段（JSON格式）
- **数据完整性**：删除图片时会同步清理对应的数据库记录和向量数据

#### 6. 图片元数据辅助生成

- **AI分析实现**：通过 `/api/v1/ai/` 路由实现
  - **端点**：
    - `POST /api/v1/ai/analyze-upload-image`：上传图片时分析
    - `POST /api/v1/ai/analyze-image-id/{image_id}`：分析已有图片
  - **实际生成内容**：基于 `backend/ai_func/` 中的实现
  - 标题：简洁主题描述（长度不做硬性截断，前端可裁剪）
  - 描述：简要语义描述
  - 标签：关键标签 JSON 数组（去空/去重）
  - **技术细节**：
    - 使用配置的 `VISION_MODEL`（默认 Qwen2.5-VL-32B-Instruct）
    - 通过兼容OpenAI格式的API调用（硅基流动等）
    - 提示词固定为文档中展示的格式
    - 结果直接更新到 `images` 表的对应字段
  - **说明**：上传流程中可直接触发分析并持久化（标题 / 描述 / 标签），当前未提供批量异步分析端点

#### 7. 实际搜索功能（基于现有实现）

- **标签搜索**：
  - 通过 `/api/v1/tags/search` 端点实现标签搜索
  - 支持标签关键词匹配和自动补全
  - 通过 `/api/v1/tags/by-tag/{tag}` 实现按标签筛选图片
- **时间筛选**：
  - 所有列表接口支持基于 `created_at` 的时间范围过滤
  - 通过 `start_date` 和 `end_date` 参数实现
- **分页与排序**：
  - 所有列表接口支持分页（page, page_size参数）
  - 支持按创建时间排序（默认为时间倒序）
**搜索能力概览**：已支持标签过滤、时间过滤、模糊搜索(`/search/fuzzy`)、统一向量检索、图片向量检索、相似检索、直接向量检索。旧文档中“未实现基于向量相似度搜索”已过时。

**后续潜力**：可扩展权重融合 / rerank / 多模态重排序（暂未内置）。

#### 8. 对话式推荐与流式事件

- 端点：`POST /api/v1/ai/recommend/chat`（非流式）、`POST /api/v1/ai/recommend/chat/stream`（SSE）
- SSE 事件：`rewrite_start` / `assistant_delta` / `complete` / `error`
- 内部 agent 产生的 `selection` 事件被聚合为 `complete`
- 向量目标白名单：`["title","description","image"]`

#### 9. 缓存统计简化

- `/system/cache` 返回目录大小（MB）、cache.db 文件大小（可选）、last_scan 时间戳
- `/system/cache/brief` 供清理后轮询确认大小归零
- 不再统计条目数量，避免磁盘文件结构差异造成误导
