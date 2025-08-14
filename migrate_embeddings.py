#!/usr/bin/env python
"""顶层迁移脚本 (主实现放这里)

执行示例:
  python migrate_embeddings.py --config backend/config/files/migration.yaml [--resume]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Iterable

PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.config.migration_config import load_migration_config  # noqa: E402
from backend.config import settings  # noqa: E402
"""注意：不要直接使用全局 encode_text / encode_image（会加载当前在线旧模型导致维度不匹配）。"""
from backend.db_func.core.extensions.loader import setup_connection  # noqa: E402

VEC_TABLES = ["title_vectors", "description_vectors", "image_vectors"]


def log(msg: str):
    print(f"[MIG] {msg}")


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False, timeout=60.0)
    conn.row_factory = sqlite3.Row
    setup_connection(conn, silent=True)
    return conn


def fetch_one(conn: sqlite3.Connection, sql: str, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    return cur.fetchone()


def exec_sql(conn: sqlite3.Connection, sql: str, params=()):
    cur = conn.cursor()
    cur.execute(sql, params)
    return cur


def create_migration_record(conn: sqlite3.Connection, old_model: str | None, new_model: str, new_dim: int):
    now = datetime.utcnow().isoformat()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO model_migrations(old_model_path, new_model_path, new_model_hash, new_embedding_dim, status, started_at, processed_images)
        VALUES(?,?,?,?, 'running', ?, 0)
        """,
        (old_model, new_model, str(hash(new_model)), new_dim, now),
    )
    conn.commit()
    return cur.lastrowid


def finalize_migration(conn: sqlite3.Connection, mig_id: int, status: str):
    now = datetime.utcnow().isoformat()
    exec_sql(conn, "UPDATE model_migrations SET status=?, finished_at=? WHERE id=?", (status, now, mig_id))
    conn.commit()


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return fetch_one(conn, "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)) is not None


def create_new_vec_tables(conn: sqlite3.Connection, dim: int, suffix: str):
    cur = conn.cursor()
    for base in VEC_TABLES:
        cur.execute(
            f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {base}{suffix} USING vec0(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER UNIQUE NOT NULL,
                embedding FLOAT[{dim}] DISTANCE_METRIC=cosine
            );
            """
        )
    conn.commit()


def truncate_tables(conn: sqlite3.Connection, tables: Iterable[str]):
    cur = conn.cursor()
    for t in tables:
        if table_exists(conn, t):
            cur.execute(f"DELETE FROM {t}")
    conn.commit()


def atomic_switch(conn: sqlite3.Connection, suffix: str):
    cur = conn.cursor()
    for base in VEC_TABLES:
        if not table_exists(conn, f"{base}{suffix}"):
            raise RuntimeError(f"临时表缺失: {base}{suffix}")
    cur.execute("BEGIN")
    try:
        for base in VEC_TABLES:
            cur.execute(f"DROP TABLE IF EXISTS {base}")
        for base in VEC_TABLES:
            cur.execute(f"ALTER TABLE {base}{suffix} RENAME TO {base}")
        # 同步重命名 vec0 影子表（如 *_chunks 等），避免扩展在查询时引用不到
        # 将 {base}{suffix}_* 重命名为 {base}_*
        for base in VEC_TABLES:
            # 查询所有与当前 base 对应且带有后缀的影子表
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?",
                (f"{base}{suffix}_%",),
            )
            rows = cur.fetchall()
            # 逐个重命名为去除后缀后的规范名
            for r in rows:
                old_name = r[0] if not isinstance(r, sqlite3.Row) else r["name"]
                # 仅在名称以 {base}{suffix}_ 前缀时处理
                prefix = f"{base}{suffix}_"
                if old_name.startswith(prefix):
                    tail = old_name[len(prefix):]
                    new_name = f"{base}_{tail}"
                    cur.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
        cur.execute("COMMIT")
    except Exception:
        cur.execute("ROLLBACK")
        raise


def insert_vec(conn: sqlite3.Connection, table: str, image_id: int, vec):
    import json as _json
    vec_json = _json.dumps(vec.tolist())
    # sqlite-vec 虚表不支持标准 UPSERT 语法，使用 INSERT OR IGNORE + UPDATE 兼容
    try:
        exec_sql(
            conn,
            f"INSERT OR IGNORE INTO {table}(image_id, embedding) VALUES (?, vec_f32(?))",
            (image_id, vec_json),
        )
        # 如果已存在（被 IGNORE），执行更新
        exec_sql(
            conn,
            f"UPDATE {table} SET embedding=vec_f32(?) WHERE image_id=?",
            (vec_json, image_id),
        )
    except sqlite3.OperationalError as e:
        # 最保守回退：尝试删除后重新插入（极少触发）
        if "unsupported" in str(e).lower() or "not implemented" in str(e).lower():
            try:
                exec_sql(conn, f"DELETE FROM {table} WHERE image_id=?", (image_id,))
                exec_sql(
                    conn,
                    f"INSERT INTO {table}(image_id, embedding) VALUES (?, vec_f32(?))",
                    (image_id, vec_json),
                )
            except Exception:
                raise
        else:
            raise


def _encode_texts_with(model, texts):
    if not texts:
        return []
    try:
        return model.encode(texts, normalize_embeddings=True, task='retrieval')
    except TypeError:
        return model.encode(texts, normalize_embeddings=True)


def _encode_images_with(model, image_paths):
    if not image_paths:
        return []
    try:
        return model.encode(image_paths, normalize_embeddings=True, task='retrieval')
    except TypeError:
        return model.encode(image_paths, normalize_embeddings=True)


def generate_for_batch(conn: sqlite3.Connection, rows, tables_map: dict, model, expected_dim: int):
    from pathlib import Path as _P
    # image batch
    img_paths, img_ids = [], []
    for r in rows:
        p = r["filepath"]
        if p and _P(p).exists():
            img_paths.append(p)
            img_ids.append(r["id"])
    if img_paths:
        img_vecs = _encode_images_with(model, img_paths)
        for iid, vec in zip(img_ids, img_vecs):
            if len(vec) != expected_dim:
                raise RuntimeError(f"图像向量维度不匹配: got {len(vec)} expect {expected_dim}")
            insert_vec(conn, tables_map["image"], iid, vec)
    # title batch
    titles = [(r["id"], (r["title"] or '').strip()) for r in rows if (r["title"] or '').strip()]
    if titles:
        text_vecs = _encode_texts_with(model, [t for _, t in titles])
        for (iid, _), vec in zip(titles, text_vecs):
            if len(vec) != expected_dim:
                raise RuntimeError(f"标题向量维度不匹配: got {len(vec)} expect {expected_dim}")
            insert_vec(conn, tables_map["title"], iid, vec)
    # description batch
    descs = [(r["id"], (r["description"] or '').strip()) for r in rows if (r["description"] or '').strip()]
    if descs:
        desc_vecs = _encode_texts_with(model, [d for _, d in descs])
        for (iid, _), vec in zip(descs, desc_vecs):
            if len(vec) != expected_dim:
                raise RuntimeError(f"描述向量维度不匹配: got {len(vec)} expect {expected_dim}")
            insert_vec(conn, tables_map["description"], iid, vec)


def clear_and_replace_cache(cache_dirs: dict):
    for _, d in cache_dirs.items():
        if not d:
            continue
        if os.path.exists(d):
            tmp_old = d + "_old"
            try:
                if os.path.exists(tmp_old):
                    shutil.rmtree(tmp_old, ignore_errors=True)
                os.rename(d, tmp_old)
            except Exception:
                shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)


def ensure_model_migrations_table(conn: sqlite3.Connection):
    """仅确保 model_migrations 表存在（避免调用全局 init_db 误操作其他库）。"""
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='model_migrations'")
    if cur.fetchone():
        return
    cur.execute('''
    CREATE TABLE IF NOT EXISTS model_migrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        old_model_path TEXT,
        new_model_path TEXT NOT NULL,
        new_model_hash TEXT NOT NULL,
        new_embedding_dim INTEGER NOT NULL,
        status TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        total_images INTEGER,
        processed_images INTEGER,
        last_image_id INTEGER,
        note TEXT
    )
    ''')
    cur.execute("CREATE INDEX IF NOT EXISTS idx_model_migrations_status ON model_migrations(status)")
    conn.commit()
    log("已创建 model_migrations 表 (局部初始化)")


def main():
    default_cfg_path = "backend/config/files/migration.yaml"
    parser = argparse.ArgumentParser(description="离线向量模型迁移")
    parser.add_argument("--config", default=default_cfg_path, help=f"迁移配置 YAML 路径 (默认 {default_cfg_path})")
    parser.add_argument("--resume", action="store_true", help="断点续传")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"配置文件未找到: {args.config} (可通过 --config 指定)" )
        return 1

    mig_conf = load_migration_config(args.config)
    cfg = settings.get_config()
    db_path = mig_conf.db_path or cfg.DB_PATH
    conn = connect(db_path)
    ensure_model_migrations_table(conn)

    running = fetch_one(conn, "SELECT * FROM model_migrations WHERE status='running' ORDER BY id DESC LIMIT 1")
    reuse = None
    if running and args.resume:
        reuse = running
        log(f"继续迁移 id={running['id']} processed={running['processed_images']} last_image_id={running['last_image_id']}")
    elif running and not args.resume:
        print("已有运行中的迁移，未加 --resume 退出")
        return 1

    from sentence_transformers import SentenceTransformer  # noqa
    import torch  # noqa
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # 某些模型支持 default_task 参数，部分（如 JinaCLIPModel）会报 unexpected keyword；做兼容回退
    try:
        new_model = SentenceTransformer(
            mig_conf.new_model_path,
            trust_remote_code=True,
            device=device,
            model_kwargs={'default_task': 'retrieval'}
        )
    except TypeError as e:
        if 'default_task' in str(e):
            log("模型不接受 default_task 参数，采用兼容加载方式")
            new_model = SentenceTransformer(
                mig_conf.new_model_path,
                trust_remote_code=True,
                device=device
            )
        else:
            raise
    # 不使用 get_sentence_embedding_dimension，优先用配置；否则用一次 encode 推断长度
    # 获取新模型维度：优先配置；否则 encode 探测；并校验一致性
    import numpy as _np
    try:
        probe = new_model.encode(["_dim_probe_"], normalize_embeddings=True, task='retrieval')
    except TypeError:
        probe = new_model.encode(["_dim_probe_"])  # 不支持 task 参数
    # 兼容 list/tuple/np.ndarray 三种返回
    if isinstance(probe, _np.ndarray):
        if probe.ndim == 1:
            if probe.shape[0] == 0:
                raise RuntimeError("无法探测新模型维度: 返回向量为空")
            probed_dim = probe.shape[0]
        elif probe.ndim >= 2:
            if probe.shape[0] == 0 or probe.shape[1] == 0:
                raise RuntimeError("无法探测新模型维度: 形状无效")
            probed_dim = probe.shape[-1]
        else:
            raise RuntimeError("无法探测新模型维度: 未知 ndarray 形状")
    elif isinstance(probe, (list, tuple)):
        if len(probe) == 0 or len(probe[0]) == 0:
            raise RuntimeError("无法探测新模型维度: 空列表")
        probed_dim = len(probe[0])
    else:
        raise RuntimeError(f"无法探测新模型维度: 不支持的返回类型 {type(probe)}")
    if mig_conf.new_embedding_dim and mig_conf.new_embedding_dim != probed_dim:
        raise RuntimeError(f"配置 new_embedding_dim={mig_conf.new_embedding_dim} 与模型实际维度 {probed_dim} 不一致")
    new_dim = mig_conf.new_embedding_dim or probed_dim
    log(f"新模型维度确认: {new_dim} (probed={probed_dim}, configured={mig_conf.new_embedding_dim})")

    current_dim = mig_conf.old_embedding_dim
    need_new = current_dim != new_dim
    suffix = '_new' if need_new else ''

    if reuse:
        mig_id = reuse['id']
    else:
        mig_id = create_migration_record(conn, mig_conf.old_model_path, mig_conf.new_model_path, new_dim)

    tables_map = {k: f"{k}_vectors{suffix}" for k in ["title", "description", "image"]}

    if need_new:
        if not reuse:
            for base in VEC_TABLES:
                leftover = f"{base}{suffix}"
                if table_exists(conn, leftover):
                    exec_sql(conn, f"DROP TABLE IF EXISTS {leftover}")
            create_new_vec_tables(conn, new_dim, suffix)
    else:
        if not reuse:
            truncate_tables(conn, tables_map.values())

    total_row = fetch_one(conn, "SELECT COUNT(*) c FROM images")
    total = total_row['c'] if total_row else 0
    if not reuse:
        exec_sql(conn, "UPDATE model_migrations SET total_images=? WHERE id=?", (total, mig_id))
        conn.commit()

    last_id = reuse['last_image_id'] if reuse and reuse['last_image_id'] else 0
    processed = reuse['processed_images'] if reuse else 0
    cur = conn.cursor()
    while True:
        cur.execute("SELECT * FROM images WHERE id>? ORDER BY id ASC LIMIT ?", (last_id, mig_conf.batch_size))
        rows = cur.fetchall()
        if not rows:
            break
        generate_for_batch(conn, rows, tables_map, new_model, new_dim)
        last_id = rows[-1]['id']
        processed += len(rows)
        exec_sql(conn, "UPDATE model_migrations SET processed_images=?, last_image_id=? WHERE id=?", (processed, last_id, mig_id))
        conn.commit()
        log(f"progress {processed}/{total} last_id={last_id}")

    if need_new:
        try:
            atomic_switch(conn, suffix)
        except Exception as e:
            finalize_migration(conn, mig_id, 'failed')
            print(f"原子切换失败: {e}")
            return 2

    clear_and_replace_cache({
        'text': cfg.TEXT_VECTOR_CACHE_DIR,
        'image': cfg.IMAGE_VECTOR_CACHE_DIR,
    })

    finalize_migration(conn, mig_id, 'completed')
    # 成功后更新主配置（模型路径与维度）
    try:
        updated = settings.update_config({
            'MODEL_PATH': mig_conf.new_model_path,
            'EMBEDDING_DIMENSION': new_dim,
        }, auto_save=True)
        if updated:
            log(f"已更新主配置: MODEL_PATH -> {mig_conf.new_model_path}, EMBEDDING_DIMENSION -> {new_dim}")
        else:
            log("主配置更新失败 (settings.update_config 返回 False)")
    except Exception as e:
        log(f"主配置更新异常: {e}")
    print('迁移完成 migration_id=', mig_id)
    return 0


if __name__ == '__main__':
    sys.exit(main())
