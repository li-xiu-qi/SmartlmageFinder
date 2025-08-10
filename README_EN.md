<div align="center">
  <img src="assets/logo/logo.png" alt="SmartImageFinder Logo" width="200">
  <h1>SmartImageFinder</h1>
  <p>Intelligent image search / management & AI conversational recommendation system</p>
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

## Overview

SmartImageFinder is a modern intelligent image search and management system. It provides unified semantic + visual retrieval (text, description, image similarity, hybrid) and a dialogue-driven AI recommendation flow. The default unified multimodal embedding model is Jina Embeddings v4 (upgrade from legacy Jina CLIP V2) offering higher-quality semantic representations.

## 🔄 Embedding Model Migration Support

We provide an offline, resumable embedding model migration script that regenerates all vectors and atomically switches tables.

Key capabilities:
- Automatic dimension probing (or respecting configured `new_embedding_dim`)
- Detect dimension change and decide strategy: create `*_vectors_new` and atomic swap OR in-place rebuild
- Batch processing with progress stored in `model_migrations` (supports `--resume`)
- Resilient SQLite vec table writes (INSERT OR IGNORE + UPDATE, no unsupported UPSERT)
- Atomic table switch (drop old, rename new) only when dimension changes
- Cache directory rotation: old cache renamed with `_old`, fresh empty caches created
- Auto-update main `config.yaml` (`MODEL_PATH`, `EMBEDDING_DIMENSION`) after successful migration

Quick usage:
```bash
# Edit backend/config/files/migration.yaml
python migrate_embeddings.py                 # run fresh migration
python migrate_embeddings.py --resume        # resume if previously interrupted
```

Before running:
1. STOP backend services (avoid concurrent writes / locks)  
2. BACKUP database: `cp data/db/smartimagefinder.db data/db/smartimagefinder.db.bak` (Windows: use `copy`)
3. Confirm new model is downloaded locally

Details & rollback guidance: see `docs/model_migration.md`.

Example `migration.yaml`:
```yaml
old_model_path: "./models/jina-embeddings-v4"   # optional record
old_embedding_dim: 2048                         # optional
new_model_path: "./models/jina-clip-v2"         # required
new_embedding_dim: 1024                         # optional (auto probe if omitted)
db_path: "./data/db/smartimagefinder.db"       # optional override
batch_size: 64                                  # optional (default 64)
```

## Features

### 🖼️ Image Management
- Browsing grid & preview
- Tagging system (multi-tag filter & management)
- Title / description / tag metadata editing
- Batch upload & batch AI analysis
- Drag & drop multi-file upload

### 🔍 Intelligent Search
- Text semantic search
- Image-to-image similarity search
- Title / description / image vector search & hybrid
- Fuzzy LIKE search for quick keyword matching
- Tag & time filtering

### 💬 Conversational Retrieval
Multi-turn dialogue-driven search workflow:
- Query rewrite + normalization
- Multi-vector retrieval (title / description / image)
- Rerank + structured SSE streaming
- Events: `rewrite_start`, repeated `assistant_delta`, final `complete`, `error`
- Conversation history trimming (64K rolling window)
- Tool-ready architecture (extendable)

### 🤖 AI Analysis
- Automatic content understanding
- Smart annotation (title / description / tags)
- Batch processing
- Pluggable multimodal model APIs

### 🎨 User Interface
- React 18 + Ant Design 5 modern UI
- Responsive layout
- Real-time editing & preview
- System status & metrics dashboard

## 🎯 Core Technical Highlights
- Dialogue recommendation agent with vector target whitelist
- Streaming SSE output for incremental UX
- SQLite + sqlite-vec lightweight high-performance vector DB
- Unified multimodal embedding model (Jina Embeddings v4)
- Disk-based vector cache (diskcache)
- One-click startup & environment bootstrap script
- Offline embedding model migration with atomic switch & resume

## 🚀 Quick Start
```bash
git clone https://github.com/li-xiu-qi/SmartImageFinder.git
cd SmartImageFinder
python start.py init   # install deps + download model + generate config
python start.py        # start frontend + backend
```
Backend default: http://localhost:10050  
Frontend default: http://localhost:5173

## Configuration (excerpt)
`backend/config/files/config.yaml`:
```yaml
MODEL_PATH: ./models/jina-embeddings-v4
VECTOR_DB_DRIVER_DIR: ./backend/config/files/vector_db_driver
EMBEDDING_DIMENSION: 2048
DB_PATH: ./data/db/smartimagefinder.db
HOST: 0.0.0.0
PORT: 10050
```

## Project Structure (simplified)
```
SmartImageFinder/
  backend/
    ai_func/
    routers/
    db_func/
    config/
  frontend/
  models/
  data/
  docs/
  migrate_embeddings.py
  start.py
```

## Verification After Migration
1. Query latest record: `SELECT status, processed_images, total_images FROM model_migrations ORDER BY id DESC LIMIT 1;` (expect `completed`)
2. Ensure no `*_new` tables remain: `SELECT name FROM sqlite_master WHERE name LIKE '%_new';` (expect empty)
3. Search (text / image / description) works
4. `config.yaml` updated with new model & dimension
5. Old cache dirs suffixed `_old` (optional cleanup)

## License
Apache 2.0 (see [LICENSE](LICENSE)).

## Contact
If you have questions or suggestions, open an issue or reach out via the WeChat QR code in the Chinese README.
