# SmartImageFinder 前端

SmartImageFinder是一个智能图像管理和搜索系统，本仓库包含系统的前端部分，基于React、TypeScript和Vite构建。

## 功能特点

- 基于文本的图像搜索
- 基于图像的相似图片搜索
- 标签管理与分类
- 图片上传与编辑
- 多模态AI分析与标注
- 系统配置管理

## 技术栈

- **框架**: React 18
- **语言**: TypeScript
- **构建工具**: Vite
- **UI组件**: Ant Design 5
- **样式**: Less
- **路由**: React Router 6
- **HTTP客户端**: Axios

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 项目结构

```
src/
  ├── assets/         # 静态资源
  ├── components/     # 公共组件
  ├── hooks/          # 自定义React Hooks
  ├── layouts/        # 布局组件
  ├── pages/          # 页面组件
  │   ├── home/       # 首页
  │   ├── images/     # 图片管理
  │   ├── search/     # 搜索页面
  │   ├── settings/   # 系统设置
  │   ├── tags/       # 标签管理
  │   └── upload/     # 上传页面
  ├── services/       # API服务
  ├── types/          # TypeScript类型定义
  └── utils/          # 工具函数
```

## 后端API

前端通过 `services/api.ts` 模块与后端API交互，主要包括以下几类接口：

- 图片管理: 上传、获取、更新、删除
- 搜索: 文本搜索、图像搜索
- 标签管理: 获取标签、添加标签、删除标签
- 系统配置: 获取配置、更新配置、清除缓存

## 开发说明

- 项目使用ESLint进行代码质量控制
- 使用Less进行样式开发
- 布局基于Ant Design的Layout组件
- 图片展示使用虚拟列表优化性能
