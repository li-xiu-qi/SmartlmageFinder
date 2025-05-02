# SmartImageFinder 向量生成设计

## 概述

向量生成是 SmartImageFinder 系统的核心组件之一，负责将图片和文本转换为高维度的数学向量（嵌入）。这些向量捕捉了内容的语义信息，使得系统能够执行基于内容的相似度搜索（如以文搜图、以图搜图）。本模块使用 `sentence-transformers` 库加载预训练的多模态模型（如 Jina CLIP V2），并提供统一的接口来编码图片和文本数据，同时集成了缓存机制以提高效率。

## 技术选型

* **库**: `sentence-transformers` - 一个用于生成句子、文本和图像嵌入的流行 Python 框架。
* **模型**: 通过配置指定，预期使用如 Jina CLIP V2 等强大的多模态模型。

## 面向对象设计

向量生成模块使用面向对象的设计，核心类是 `VectorEncoder`。这个类负责:

1. 懒加载模型
2. 维护缓存实例
3. 提供文本和图像的向量编码功能

## 配置系统

向量生成模块的行为可通过以下配置项控制：

1. `MODEL_PATH`: 指定要使用的预训练模型路径
2. `TEXT_VECTOR_CACHE_DIR`: 文本向量缓存目录
3. `IMAGE_VECTOR_CACHE_DIR`: 图像向量缓存目录
4. `USE_CACHE`: 是否启用向量缓存功能

这些配置可以通过环境变量（前缀为 `SMARTIMAGEFINDER_`）或 `.env` 文件进行定制。

```python

```
