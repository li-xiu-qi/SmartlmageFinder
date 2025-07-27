# AI智能图片推荐服务

基于SmartImageFinder的AI智能推荐系统，提供检索增强生成(RAG)的图片推荐功能。

## 🚀 快速启动

### 1. 安装依赖
```bash
cd ai_backend
pip install -r requirements.txt
```

### 2. 配置环境变量
编辑 `.env` 文件：
```bash
OPENAI_API_KEY=your-openai-api-key
```

### 3. 启动服务
```bash
python main.py
```

服务将在 http://localhost:10051 启动

## 📋 API接口文档

### 1. AI智能推荐
```http
POST /api/v1/ai/recommend?query=美丽风景&search_type=text&limit=10&include_ai_reasoning=true
```

### 2. 对话接口
```http
POST /api/v1/ai/chat
Content-Type: application/json

{
  "message": "这些图片有什么共同点？",
  "context_images": [1, 2, 3]
}
```

### 3. 快速搜索
```http
GET /api/v1/ai/quick-search?query=日落&limit=8
```

## 🎯 功能特性

- ✅ **智能图片推荐**：基于AI的内容分析
- ✅ **检索增强生成**：结合搜索结果的RAG
- ✅ **边缘情况处理**：无意义标题/描述的优化
- ✅ **相似度校正**：AI重新评估相关性
- ✅ **多维度搜索**：文本、向量、相似、过滤
- ✅ **实时对话**：基于图片内容的智能对话

## 🔧 技术架构

```
ai_backend/
├── app/
│   ├── config.py          # 配置管理
│   ├── models/
│   │   └── schemas.py     # 数据模型
│   ├── services/
│   │   ├── search_client.py    # 后端API调用
│   │   ├── ai_service.py       # OpenAI集成
│   │   └── recommendation_service.py  # 推荐逻辑
│   └── routers/
│       └── ai_recommendations.py  # API路由
└── main.py               # 应用入口
```

## 🎨 前端集成

前端页面已创建在 `ai_frontend/src/pages/ai/AIPage.tsx`，包含：
- 智能搜索界面
- 结果展示卡片
- AI推荐理由显示
- 响应式布局