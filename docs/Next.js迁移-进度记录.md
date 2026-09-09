# Next.js 全栈迁移 · 进度记录

> 最后更新：2026-09-09
> 状态：Phase 3 核心 API 已打通，待前端迁移

## 架构定论

```
Next.js(TS, 本机:3000) = 前端 + 业务 API
    ↓ HTTP (base64 图片 / JSON 向量)
Python 推理服务 (dgx-spark:8100) = jina 编码 + sqlite-vec + glm 图像分析
    ↓ 直接读写
SQLite (dgx-spark, scp 到本机)
```

## 已解决的关键问题

### 1. 本机 DB 实情
- 本机 `data/smartimager.db` 曾是空库（4096 字节），之前「/api/v1/images 返回数据」是误读，返回的是空数组
- 已 scp 远程 DB（8577024 字节，24 张图）覆盖本地空库，`GET /api/v1/images` 现在返回真实 24 条

### 2. 上传链路（formidable → busboy）
- Next.js 16 的 `formData()` API 在 webpack 模式下 `_transform() method is not implemented`
- `formidable` 同样报 `_transform() method is not implemented`
- 最终用 `busboy`（Next.js 内部同款）解析 multipart，稳定

### 3. 图片传输：本机路径 → base64
- 远程 jina 和 glm 都读不到本机 Windows 路径
- `inference.ts` 的 `encodeImage` 改为：本机读文件 → base64 data URI → 发远程
- 远程 `/encode` 和 `/analyze` 都改为支持 `data:image/...;base64,...` 前缀

### 4. rewrites 路径
- 远程推理服务路由是 `/encode`、`/analyze`、`/vectors/*`，没有 `/api/v1` 前缀
- `next.config.js` rewrites 改为逐条映射，去掉 `/api/v1` 前缀

### 5. GLM_API_KEY 传递
- `setsid nohup` 启动时环境变量不继承，`$GLM_API_KEY` 在远程 SSH 会话里是空的
- 改为从 `~/SmartImager_new/backend/config/files/config.yaml` 的 `OPENAI_API_KEY` 字段读取，启动时显式传入

### 6. Next.js 动态路由 slug
- `images/[image_id]` 与 `images/upload` 冲突（不同 slug 名），报错
- 统一改为 `images/[id]`

## 已验证通的 API

| 方法 | 路径 | 状态 |
|------|------|------|
| GET | /api/v1/images | ✅ 分页列表 |
| GET | /api/v1/images/[id] | ✅ 详情 |
| PUT | /api/v1/images/[id] | ✅ 更新字段 |
| DELETE | /api/v1/images/[id] | ✅ 删除 + 删向量 + 删文件 |
| POST | /api/v1/images/upload | ✅ 上传 + AI 分析 + 向量化 |
| GET | /api/v1/tags | ✅ 标签统计 |
| GET | /api/v1/search/similar/[id] | ✅ 向量相似搜索 |
| GET | /api/v1/system | ✅ 系统状态 |

## 未解决

- 上传后本地 DB 有新记录，远程 DB 没有（数据单向流动），后续需回传方案
- AI 对话相关路由（ai/conversations 等）未迁
- 前端 7 个页面：**已全部迁移完成**（2026-09-09），详见 MIGRATION-NOTES.md
- 旧 FastAPI:8000：**已于 2026-09-09 下线**（回退记录在 dgx-spark `~/SmartImager_new/legacy_backend_retired.md`）

### 未解决的问题（不影响使用，后续可处理）
- 文本语义搜索接口（`GET /api/v1/search/unified`）和上传图片搜索接口（`POST /api/v1/search/unified/image`）未实现，search 页已预留接入开关
- AI 对话相关路由（ai/conversations 等）未迁
- 上传后本地 DB 有新记录，远程 DB 没有（数据单向流动），后续需回传方案
- 本地 `data/` 目录与远程 DB 的同步/挂载方案未定（当前靠 scp 手动同步）

## 启动命令速查

推理服务（dgx-spark，kill 和启动必须分两次 SSH）：
```bash
ssh ke@192.168.1.170 'PIDS=$(pgrep -f "inference_service/main.py"); [ -n "$PIDS" ] && kill $PIDS; sleep 3'
# 另起一条
ssh ke@192.168.1.170 '
DB=$(find ~/SmartImager_new -name "*.db" -not -path "*/.venv/*" | head -1)
KEY=$(grep "OPENAI_API_KEY" ~/SmartImager_new/backend/config/files/config.yaml | awk "{print \$2}")
MODEL_PATH="/home/ke/.cache/huggingface/hub/models--jinaai--jina-embeddings-v4/snapshots/853c867b65b749f3c3c72a06868140d842e04f06" \
VECTOR_DB_PATH="$DB" \
VECTOR_DB_DRIVER="/home/ke/SmartImager_new/backend/config/files/vector_db_driver/sqlite-vec-0.1.6-loadable-linux-aarch64/vec0.so" \
INFERENCE_PORT=8100 \
GLM_API_KEY="$KEY" \
setsid nohup /home/ke/SmartImager_new/.venv/bin/python ~/SmartImager_new/inference_service/main.py > /tmp/inference_service.log 2>&1 < /dev/null & disown'
```

Next.js dev server（本机）：
```bash
cd .../next-app
PID=$(netstat -ano | grep ":3000" | grep LISTENING | awk '{print $NF}' | head -1)
[ -n "$PID" ] && taskkill //F //T //PID $PID   # 注意 //T 杀进程树
NODE_ENV=development npx next dev --port 3000 --webpack
```
