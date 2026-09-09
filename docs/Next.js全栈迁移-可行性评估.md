# Next.js 全栈迁移 · 可行性评估

> 创建时间：2026-09-08
> 状态：评估阶段，供决策参考
> 结论：**不推荐全量迁移**，推理层必须保留 Python

---

## 1. 当前技术栈

| 层 | 技术 | 代码量 |
|----|------|--------|
| 前端 | React 18 + Vite + TypeScript + shadcn/ui + Tailwind + antd | SPA，多页面 |
| 主后端 | FastAPI + SQLAlchemy + SQLite | ~7806 行业务代码（不含 tests） |
| 推理层 | jina-embeddings-v4 (transformers + PyTorch + Qwen2.5-VL) | 本地 GPU 推理 |
| 向量存储 | sqlite-vec | SQLite 扩展 |
| 视觉模型 | glm-4.6v-flash（云端 API） | 无本地依赖 |

---

## 2. 硬障碍：推理层无法迁移

以下三项是 Python 生态专属，Node.js 无等效替代：

### 2.1 jina-embeddings-v4 模型

- 架构：transformers + PyTorch + Qwen2.5-VL 定制（非标准 SentenceTransformer）
- 现状：在 HF 缓存里手动打过补丁（`modeling_jina_embeddings_v4.py`、`qwen2_5_vl.py` 的 RoPE 修复）
- Node 生态：无等效方案。ONNX Runtime 理论上可加载，但 Qwen2.5-VL + 定制代码的转换成本极高，且补丁逻辑无法直接迁移

### 2.2 sqlite-vec 向量存储

- 现状：通过 `load_extension` 加载原生 `.so`，配合 SQLAlchemy repository 做向量检索
- Node 生态：`sqlite-vec` 官方有 Node binding，但现有 356 行的 `vectors.py` repository 逻辑需要重写，且 64 位 ARM 版 `.so` 的获取和维护在 Node 侧没有现成方案

### 2.3 本地模型推理

- 现状：PyTorch + CUDA + bfloat16，在 dgx-spark (GB10 GPU) 上运行
- Node 生态：无等效方案

**结论**：推理层（模型加载、编码、向量检索）必须保留 Python。这正是《推理服务独立-拆分设计》要拆出去的部分。

---

## 3. 可迁移部分：业务层

理论上可迁 Next.js 的模块：

| 模块 | 行数 | 迁移难度 | 说明 |
|------|------|---------|------|
| routers/images.py | 570 | 中 | CRUD + 文件上传，Next.js API Routes 可替代 |
| routers/search/ | 554 | 中 | 搜索编排，调推理服务 + 本地向量存储 |
| routers/ai/recommendation.py | 244 | 中 | AI 推荐，调推理服务 + 向量检索 |
| routers/tags.py | 161 | 低 | 标签 CRUD |
| routers/metadata.py | - | 低 | 元数据 CRUD |
| routers/system.py | 129 | 低 | 状态接口 |
| db_func/repositories/ | ~1500 | 中 | SQLAlchemy → Prisma/Drizzle |
| db_func/core/ | ~500 | 中 | 连接池、数据库初始化 |
| config/ | ~485 | 低 | Pydantic Settings → Zod |
| ai_func/image_analysis.py | 213 | 低 | 调云端 glm-4.6v-flash API，OpenAI SDK 有 Node 版 |
| system_fun/ | ~470 | 低 | 缓存、配置管理 |

**可迁行业务代码估算**：~4500-5000 行（不含推理层和向量存储）

---

## 4. 迁移成本估算

| 阶段 | 工作量 | 风险 |
|------|--------|------|
| Next.js 项目初始化 + shadcn/ui 迁移 | 2-3 天 | 低 |
| API Routes 重写（CRUD + 文件上传） | 3-5 天 | 低 |
| 数据库层迁移（Prisma schema + repository 重写） | 3-5 天 | 中（SQLAlchemy → Prisma 语义差异） |
| 搜索/推荐链路改造（调推理服务 HTTP） | 2-3 天 | 中 |
| 向量检索逻辑重写（sqlite-vec Node binding） | 3-5 天 | **高**（ARM .so 获取、repository 重写） |
| 联调 + 回归测试 | 3-5 天 | 中 |
| **合计** | **16-26 天** | - |

---

## 5. 收益分析

### 5.1 潜在收益

- 全栈 TypeScript，类型安全贯穿前后端
- Next.js 部署简单（Vercel / Docker）
- 前端已在 React 上，组件可复用
- 消除 Python 后端的 import 开销（fastify/Next.js 启动 <1s）

### 5.2 实际收益评估

| 收益 | 实际价值 | 说明 |
|------|---------|------|
| 启动速度 | 低 | 推理服务独立后主后端已是 ~1-2s，再迁 Node 边际收益很小 |
| 类型安全 | 中 | 有价值，但当前前后端分离 + OpenAPI 已能生成类型 |
| 部署简化 | 低 | 当前 Docker 部署已足够简单 |
| 开发体验 | 中 | 统一语言，但团队只有 1 人，边际收益有限 |
| 性能 | 低 | 项目规模小，Node vs Python 性能差异不显著 |

---

## 6. 风险评估

| 风险 | 等级 | 说明 |
|------|------|------|
| sqlite-vec Node binding 在 ARM 上的稳定性 | **高** | 需要自行编译或找到 64 位 ARM .so，无现成方案 |
| SQLAlchemy → Prisma 语义差异 | 中 | 复杂查询、连接池、事务语义需要逐一验证 |
| 文件上传/临时文件处理差异 | 低 | Next.js API Routes 有成熟方案 |
| 回归测试覆盖不足 | 中 | 当前 tests 覆盖率未知，迁移后需全面回归 |
| 双栈维护期 | 中 | 迁移期间 Python 和 Node 并存，增加维护成本 |

---

## 7. 结论与建议

### 7.1 不推荐全量迁移 Next.js

核心原因：
1. **推理层锁死 Python**，不存在"全转 TS"
2. 业务层迁移 16-26 天工作量，收益不确定
3. 最高风险项（sqlite-vec ARM .so）没有现成方案
4. 当前 FastAPI 跑得没问题，性能对小项目不敏感

### 7.2 推荐路径

**先做推理服务独立**（见《推理服务独立-拆分设计.md》），这已经解决了启动慢和故障隔离两个核心痛点。

如果后续确有全栈 TS 需求，再考虑**混合架构**：

```
┌─────────────────┐     HTTP      ┌──────────────────┐
│  Next.js (TS)   │──────────────▶│ 推理服务 (Python) │
│  前端 + BFF     │               │  jina + sqlite-vec│
│  业务 API Routes │               └──────────────────┘
└─────────────────┘
```

即：Next.js 承担前端 + 业务 API（CRUD、文件、搜索编排），Python 只保留推理服务（模型 + 向量存储）。

### 7.3 触发迁移的条件

满足以下**至少两条**时才值得启动迁移评估：

- [ ] 团队扩大到 2 人以上，需要统一技术栈降低协作成本
- [ ] 需要部署到 Vercel / Serverless 环境
- [ ] 业务逻辑复杂度显著增长，TypeScript 类型安全成为瓶颈
- [ ] 当前 Python 后端出现无法解决的功能/性能瓶颈

---

## 8. 待确认事项

- [ ] 当前 tests 覆盖率（影响迁移风险评估）
- [ ] 是否有 Vercel / Serverless 部署计划
- [ ] 团队规模是否计划扩大
- [ ] sqlite-vec Node ARM .so 是否有可用来源（需要进一步调研）
