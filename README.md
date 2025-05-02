# SmartImageFinder

个人本地使用的智能图片管理系统，基于 AI 技术实现图片分析和智能搜索。

## 功能特点

- 基于文本的图片语义搜索
- 基于图片的相似图片搜索
- 自动生成图片标题、描述和标签
- 支持按标签和元数据筛选图片
- 适用于本地存储的图片集合管理

## 技术栈

- **后端**: FastAPI, Python 3.10+
- **前端**: React 18, Ant Design 5
- **向量数据库**: Faiss
- **向量生成**: Jina CLIP V2
- **多模态内容生成**: OpenAI Vision API

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+

### 后端设置

1. 安装依赖:

```bash
cd backend
pip install -r requirements.txt
```

2. 复制环境变量示例并编辑:

```bash
cp .env.example .env
# 编辑 .env 文件填写必要的配置
```

3. 启动Milvus (使用Docker):

```bash
docker-compose up -d
```

4. 启动后端服务器:

```bash
cd backend
python app.py
```

服务将在 http://localhost:8000 上运行，API文档可在 http://localhost:8000/docs 上查看。

### 前端设置

1. 安装依赖:

```bash
cd frontend
npm install
```

2. 启动开发服务器:

```bash
npm run dev
```

前端将在 http://localhost:3000 上运行。

## 项目结构

```
SmartImageFinder/
├── backend/                  # 后端代码
│   ├── api/                  # API路由
│   ├── core/                 # 核心组件
│   ├── services/             # 业务服务
│   ├── utils/                # 工具函数
│   ├── app.py               # 应用入口
│   └── requirements.txt     # 依赖项
├── frontend/                 # 前端代码
│   ├── public/               # 静态资源
│   ├── src/                  # 源代码
│   └── package.json          # 依赖配置
├── data/                     # 数据存储目录
├── cache/                    # 缓存目录
├── docs/                     # 文档目录
└── README.md                 # 项目说明
```

## 文档

更多详细信息，请参阅 [docs/](./docs/) 目录下的文档。

## 许可证

[MIT](LICENSE)
