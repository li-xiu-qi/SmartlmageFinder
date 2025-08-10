#!/usr/bin/env python3
"""
重建当前数据库全部图片的向量数据脚本。
功能:
1. 检查并输出 sqlite-vec 扩展版本、向量表结构是否为 VIRTUAL TABLE vec0.
2. 统计现有 images / 各向量表行数.
3. 为缺失向量的图片批量生成 (图像/标题/描述) 向量, 支持分批.
4. 可选 --force 重新生成(覆盖)已有向量.
5. 生成完成后做一次简单向量搜索验证.

使用:
python rebuild_all_vectors.py [--batch-size 32] [--force]

要求: 已正确配置 config.yaml, 且模型已就绪 (MODEL_PATH 指向 sentence-transformers 兼容模型).
"""
import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import List, Dict

# 项目根目录加入路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import settings  # noqa: E402
from backend.ai_func.generate_vector import encode_text, encode_image, get_embedding_dimension  # noqa: E402
from backend.db_func.core.connection import get_db_connection  # noqa: E402
from backend.db_func.core.database import init_db  # noqa: E402
from backend.db_func.core.extensions.loader import setup_connection  # noqa: E402
from backend.db_func.repositories.images import ImageRepository  # noqa: E402
from backend.db_func.repositories.vectors import VectorRepository  # noqa: E402


def fetch_table_info(conn: sqlite3.Connection, table: str):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception:
        return None


def is_virtual_vec_table(create_sql: str | None) -> bool:
    if not create_sql:
        return False
    normalized = create_sql.lower()
    return "virtual" in normalized and "using vec0" in normalized


def get_counts(conn: sqlite3.Connection):
    cur = conn.cursor()
    counts = {}
    for t in ["images", "title_vectors", "description_vectors", "image_vectors"]:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            counts[t] = cur.fetchone()[0]
        except Exception as e:
            counts[t] = f"ERR: {e}"  # table 不存在
    return counts


def load_images() -> List[Dict]:
    repo = ImageRepository()
    images, total = repo.get_list(page=1, page_size=100000)  # 取全部
    return images


def vector_missing(conn: sqlite3.Connection, table: str, image_id: int) -> bool:
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM {table} WHERE image_id=?", (image_id,))
    return cur.fetchone() is None


def generate_for_batch(images_batch: List[Dict], force: bool, conn: sqlite3.Connection):
    """对一个批次生成向量(图像+标题+描述). 图像批量; 文本分批."""
    if not images_batch:
        return 0, 0, 0

    # --- 图像向量批量 ---
    image_repo = VectorRepository()
    cur = conn.cursor()

    image_paths = []
    image_ids = []
    for img in images_batch:
        if not force and not vector_missing(conn, 'image_vectors', img['id']):
            continue
        if img.get('filepath') and Path(img['filepath']).exists():
            image_paths.append(img['filepath'])
            image_ids.append(img['id'])
    added_image = 0
    if image_paths:
        vectors = encode_image(image_paths)  # 返回与 paths 对应的 list/ndarray
        for iid, vec in zip(image_ids, vectors):
            vec_json = json.dumps(vec.tolist())
            cur.execute("INSERT INTO image_vectors(image_id, embedding) VALUES (?, vec_f32(?)) ON CONFLICT(image_id) DO UPDATE SET embedding=excluded.embedding", (iid, vec_json))
            added_image += 1
        conn.commit()

    # --- 文本(标题/描述) ---
    added_title = 0
    added_desc = 0
    title_items = []
    title_ids = []
    desc_items = []
    desc_ids = []
    for img in images_batch:
        title = (img.get('title') or '').strip()
        desc = (img.get('description') or '').strip()
        if title:
            if force or vector_missing(conn, 'title_vectors', img['id']):
                title_items.append(title)
                title_ids.append(img['id'])
        if desc:
            if force or vector_missing(conn, 'description_vectors', img['id']):
                desc_items.append(desc)
                desc_ids.append(img['id'])

    if title_items:
        title_vecs = encode_text(title_items)
        for iid, vec in zip(title_ids, title_vecs):
            vec_json = json.dumps(vec.tolist())
            cur.execute("INSERT INTO title_vectors(image_id, embedding) VALUES (?, vec_f32(?)) ON CONFLICT(image_id) DO UPDATE SET embedding=excluded.embedding", (iid, vec_json))
            added_title += 1
    if desc_items:
        desc_vecs = encode_text(desc_items)
        for iid, vec in zip(desc_ids, desc_vecs):
            vec_json = json.dumps(vec.tolist())
            cur.execute("INSERT INTO description_vectors(image_id, embedding) VALUES (?, vec_f32(?)) ON CONFLICT(image_id) DO UPDATE SET embedding=excluded.embedding", (iid, vec_json))
            added_desc += 1
    if added_title or added_desc:
        conn.commit()

    return added_image, added_title, added_desc


def ensure_db_initialized():
    """确保数据库与扩展已初始化 (幂等)."""
    try:
        init_db()  # 幂等: 使用 IF NOT EXISTS
    except Exception as e:
        print(f"init_db 执行异常: {e}")


def rebuild_all(batch_size: int, force: bool):
    config = settings.get_config()
    db_path = config.DB_PATH
    print(f"数据库路径: {db_path}")

    # 初始化 (表 + 初次加载扩展)
    ensure_db_initialized()

    with get_db_connection() as conn:
        # 为当前连接加载扩展 (get_db_connection 不会自动加载)
        try:
            setup_ok = setup_connection(conn, silent=True)
            if not setup_ok:
                print("警告: 本次连接未能加载 sqlite-vec 扩展，后续 vec 功能可能失败。")
        except Exception as e:
            print(f"加载扩展到当前连接失败: {e}")
        # 基础信息
        try:
            c = conn.cursor()
            c.execute("SELECT vec_version()")
            print("向量扩展版本:", c.fetchone()[0])
        except Exception as e:
            print("无法读取vec_version():", e)

        table_sqls = {t: fetch_table_info(conn, t) for t in ["title_vectors", "description_vectors", "image_vectors"]}
        for t, sql in table_sqls.items():
            print(f"表 {t} 结构: {'OK(VIRTUAL vec0)' if is_virtual_vec_table(sql) else '不正确或不存在'}")
            if sql:
                print(f"  CREATE SQL: {sql}")

        counts_before = get_counts(conn)
        print("生成前计数:", counts_before)

        images = load_images()
        print(f"发现图片数量: {len(images)}")
        if not images:
            print("无图片记录，结束")
            return

        total_added_img = total_added_title = total_added_desc = 0
        for i in range(0, len(images), batch_size):
            batch = images[i:i+batch_size]
            a_img, a_title, a_desc = generate_for_batch(batch, force, conn)
            total_added_img += a_img
            total_added_title += a_title
            total_added_desc += a_desc
            print(f"批次 {i//batch_size +1}: image={a_img}, title={a_title}, desc={a_desc}")

        counts_after = get_counts(conn)
        print("生成后计数:", counts_after)
        print(f"新增/覆盖 图像向量:{total_added_img}, 标题向量:{total_added_title}, 描述向量:{total_added_desc}")

        # 简单验证: 若存在至少一条标题向量, 做一次相似度检索
        try:
            cur = conn.cursor()
            cur.execute("SELECT image_id FROM title_vectors LIMIT 1")
            row = cur.fetchone()
            if row:
                test_query = "测试"
                q_vec = encode_text(test_query)
                # sqlite-vec MATCH 语法
                cur.execute("SELECT image_id, distance FROM title_vectors WHERE embedding MATCH vec_f32(?) ORDER BY distance LIMIT 5", (json.dumps(q_vec.tolist()),))
                results = cur.fetchall()
                print("示例检索结果 (title_vectors, query=测试):")
                for r in results:
                    print(dict(r))
        except Exception as e:
            print("示例检索失败:", e)


def main():
    parser = argparse.ArgumentParser(description="重建全部图片向量")
    parser.add_argument('--batch-size', type=int, default=32, help='批处理大小')
    parser.add_argument('--force', action='store_true', help='强制重新生成已有向量')
    parser.add_argument('--no-init', action='store_true', help='跳过 init_db (已确保初始化时可用)')
    args = parser.parse_args()

    print(f"参数: batch_size={args.batch_size}, force={args.force}")
    rebuild_all(args.batch_size, args.force)


if __name__ == '__main__':
    main()
