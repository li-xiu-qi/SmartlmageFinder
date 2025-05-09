# SmartImageFinder 项目设计指南

## 项目概述

SmartImageFinder 是一个基于 Jina CLIP V2 模型的个人使用的智能图片管理与检索系统。该系统集成了 FastAPI faiss 向量数据库、React + Ant Design 前端框架，并结合硅基流动多模态模型 API，提供全面的图片智能管理解决方案。**本系统设计为本地桌面Web应用，专为个人使用场景优化，因此，极致的性能扩展和复杂的网络优化并非核心设计目标，重点在于功能的完整性和个人用户的易用性。**

### 核心功能

**所有检索模式均支持时间过滤功能**，用户可以基于图片上传时间属性进行筛选，支持时间范围查询和相对时间（如"最近一周"、"最近一个月"）过滤。

此外，系统还提供图片基于标签的分类管理、元数据管理等辅助功能，为用户提供全方位的图片资源管理体验。
系统支持两种主要检索模式：

#### 检索模式

1. **非向量检索模式**
   - 基于传统文本匹配的检索方式
   - 支持对图片自定义标题和描述的精确/模糊匹配
   - 适用于关键词精确查找场景
   - **元数据检索功能**：
     - 基于图片元数据的文本匹配检索
     - 元数据值仅支持字符串数据类型
     - 默认系统会为图片添加标题和描述作为基础元数据
     - 支持多种元数据类型的组合查询和筛选
     - **元数据字段动态发现**：系统通过专用 API 动态分析存储在 Faiss 中的元数据字段，提取所有可用字段并提供使用频率统计，自动构建元数据过滤界面使用的字段
   - 适合精确查找和结构化数据筛选场景

2. **向量检索模式**
   - **文本-图片匹配**：将用户输入的文本通过[向量生成模块](./vector_generation.md)转换为向量，与图片标题/描述向量或图片本身的视觉向量进行相似度计算
   - **文本-文本匹配**：将用户输入的文本通过[向量生成模块](./vector_generation.md)转换为向量，与系统中存储的图片标题和描述文本向量进行语义相似度匹配
   - **图片-图片匹配**：上传参考图片，通过[向量生成模块](./vector_generation.md)将其转换为向量后与库中图片进行相似度匹配
   - 基于 Faiss 实现高效的向量近邻搜索与过滤
   - 利用 Jina CLIP V2 多模态模型实现文本和图片的语义对齐
   - **向量生成**：
     - 所有向量及其元数据统一存储在 Faiss 中
     - 使用图片/文本哈希值作为唯一标识符

#### 图片管理

3. **图片管理功能**
    - 提供专门的图片浏览和管理页面
    - 以网格式布局展示图片，每个图片以卡片形式呈现
    - 每个图片卡片包含：
      - 图片预览（直接使用原图）
      - 基本信息（标题、上传日期等）
      - 快捷操作按钮（编辑、放大、以当前图搜图、删除）
    - 支持图片详情查看、批量操作和按照标签分类整理
    - 提供图片信息编辑功能，包括修改标题、描述、标签和其他元数据，其中标题、描述、标签也是元数据
    - 点击"以图搜图"可直接以当前图片为基础进行相似图片搜索
    - **交互式标签筛选功能**：
      - 页面展示所有可用标签，支持点击标签进行筛选
      - 点击标签会"点亮"该标签，系统自动筛选包含该标签的图片
      - 支持多标签同时选择，实现组合筛选效果
      - 显示每个标签对应的图片数量统计
      - 提供标签快速取消和全部清除选项
      - 标签筛选可与其他检索条件（如时间、元数据）组合使用
    - **优化的图片加载策略**：
      - 利用Ant Design的Image组件实现懒加载和渐进式加载
      - 图片浏览采用虚拟滚动技术，确保大量图片浏览时的流畅体验
      - **针对本地使用场景优化，无需生成和管理缩略图，优先保证功能实现而非极致加载性能。**

#### 图片上传与处理

4. **批量上传与智能处理**
   - 支持多种上传方式：
     - 拖放上传多个图片文件
     - 文件选择器批量选择上传
     - 本地文件路径导入
   - **批量处理功能**：
     - 提供"AI批量分析"按钮，一键处理所有上传的图片
     - 后台异步处理，显示进度条和完成状态
     - 支持在上传过程中添加公共元数据，应用于所有图片
   - **个性化处理**：
     - 每个图片容器提供独立的"AI分析"按钮，可单独分析当前图片
     - 智能生成三个默认元数据：图片标题、图片描述、图片标签
     - 支持为每个图片单独添加自定义元数据字段和值
     - 提供直观的元数据编辑界面，支持添加、修改、删除操作
   - **上传预览与编辑**：
     - 使用Ant Design Upload组件前端预览功能
     - 允许在上传前调整图片元数据
     - 提供批量标签应用功能，快速为多张图片添加相同标签
   - **上传状态跟踪**：
     - 显示每张图片的处理状态和进度
     - 提供失败重试和取消上传选项
     - 完成后显示成功/失败统计和摘要信息
   - **数据入库流程**：
     - 图片文件保存至文件系统，直接保存到对应的目录下即可。
     - 调用[向量生成模块](./vector_generation.md)计算图片向量和文本向量。
     - 调用[多模态内容生成模块](./multimodal_generation.md)生成元数据（标题、描述、标签）。
     - 图片向量和所有元数据统一存入 Faiss 向量数据库 (参考 [数据库设计](./database_design.md))。

#### 图片存储与文件管理

7. **图片存储与文件管理策略**
   - **UUID命名策略**：
     - 为每张上传的图片自动生成UUID作为唯一标识符
     - 将UUID转换为十六进制形式，作为文件存储名称和 Faiss 主键
     - 完全替代原始文件名，避免任何命名冲突问题
     - 原始文件名作为元数据保存，便于检索和显示
   - **图片访问优化**：
     - 本地文件系统直接访问，无需网络传输优化
     - 利用Ant Design的图片组件进行前端优化：懒加载、渐进式加载
     - 使用虚拟滚动，仅加载视口内的图片，优化大量图片浏览的性能
   - **元数据关联**：
     - Faiss 中通过UUID关联图片文件和其元数据
     - 保存原始文件名、文件类型、大小等基本信息作为标量字段
     - 记录图片在文件系统中的相对路径
     - 同时存储图片向量和文本向量，支持多种相似度查询

#### 图片元数据辅助生成

5. **多模态内容生成**
   - 基于硅基流动多模态模型 API 自动为图片生成：
     - **智能标题**：根据图片内容自动创建描述性标题
     - **详细描述**：生成对图片内容的全面、准确描述
     - **语义标签**：提取图片中的关键元素作为分类标签
   - 支持批量处理功能，可对新导入的图片集合自动应用内容生成
   - 用户可对生成的内容进行编辑和调整
   - 生成的标题、描述和标签与向量检索功能无缝集成，提升搜索体验
   - 支持多语言内容生成，满足不同语言环境的用户需求
   - 使用以下优化提示词引导模型生成高质量内容：

     ```python
     DESCRIPTION_PROMPT = """
     请分析这张图片并生成一个10字以内的标题、50字以内的图片描述和5个关键标签，使用JSON格式输出。

     分析以下方面:
     1. 图像类型（图表、示意图、照片等）
     2. 主要内容/主题
     3. 包含的关键信息点
     4. 图像的可能用途

     输出格式必须严格为:
     {
       "title": "简洁标题(10字以内)",
       "description": "详细描述(50字以内)",
       "tags": ["标签1", "标签2", "标签3", "标签4", "标签5"]
     }

     只返回JSON，不要有其他说明文字。
     """
     ```
