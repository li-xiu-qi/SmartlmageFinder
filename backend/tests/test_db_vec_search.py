import sqlite3
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import os
import json
import pickle
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances



# 首先尝试加载本地模型
model_path = r'C:\Users\k\Desktop\BaiduSyncdisk\baidu_sync_documents\hf_models\bge-m3'
model = SentenceTransformer(model_path)
print(f"成功加载本地模型: {model_path}")


# 获取模型的输出维度
embedding_dim = model.get_sentence_embedding_dimension()
print(f"模型输出维度: {embedding_dim}")


# 创建一个SQLite数据库连接
db_path = "vec.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# 尝试加载sqlite-vec扩展
try:
    conn.enable_load_extension(True)
    # 根据操作系统加载不同的扩展文件
    conn.execute("SELECT load_extension('./vec0.dll')")
    # 测试扩展是否成功加载
    cursor.execute("SELECT vec_version()")
    version = cursor.fetchone()[0]
    print(f"成功加载sqlite-vec扩展，版本: {version}")
except Exception as e:
    print(f"加载sqlite-vec扩展失败: {e}")
    print("将使用纯Python实现向量操作")
    print("如需使用sqlite-vec扩展，请从 https://github.com/asg017/sqlite-vec/releases 下载对应版本")
    
    
    
# 创建向量表和元数据表
# 首先删除已存在的表
cursor.execute("DROP TABLE IF EXISTS doc_metadata")
cursor.execute("DROP TABLE IF EXISTS vec_embeddings")

# 创建向量表 - 专门用于存储和检索向量
cursor.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS vec_embeddings USING vec0(
                    document_id INTEGER PRIMARY KEY,
                    content_embedding FLOAT[{embedding_dim}] DISTANCE_METRIC=cosine
                );
                """)

# 创建元数据表 - 用于存储文档的元数据信息
cursor.execute("""
                CREATE TABLE IF NOT EXISTS doc_metadata(
                    document_id INTEGER PRIMARY KEY,
                    original_content TEXT,
                    category TEXT,
                    created_at TIMESTAMP,
                    tags TEXT,
                    FOREIGN KEY(document_id) REFERENCES vec_embeddings(document_id)
                );
                """)


def insert_documents(cursor, documents):
    # 清空表
    cursor.execute("DELETE FROM vec_embeddings")
    cursor.execute("DELETE FROM doc_metadata")
    
    for doc in documents:
        embedding_json = json.dumps(doc["embedding"].tolist())
        try:
            # 1. 先插入向量数据
            cursor.execute(
                "INSERT INTO vec_embeddings(document_id, content_embedding) VALUES (?, vec_f32(?))",
                (doc["id"], embedding_json)
            )
            
            # 2. 再插入元数据
            cursor.execute(
                "INSERT INTO doc_metadata(document_id, original_content, category, created_at, tags) VALUES (?, ?, ?, ?, ?)",
                (doc["id"], doc["content"], doc["category"], doc.get("created_at"), 
                 json.dumps(doc.get("tags", [])) if "tags" in doc else None)
            )
        except Exception as e:
            print(f"插入数据失败: {e}")
            
# 准备一些示例文本
from datetime import datetime, timedelta

# 生成时间戳，从当前时间倒推
base_time = datetime.now()
# 使用更易读的时间格式，去掉ISO 8601格式中的"T"分隔符
def format_datetime(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

documents = [
    {"id": 1, "content": "机器学习是人工智能的一个子领域", "category": "技术", 
     "created_at": format_datetime(base_time - timedelta(days=10)),
     "tags": ["机器学习", "AI", "人工智能"]},
    
    {"id": 2, "content": "深度学习是机器学习的一种方法", "category": "技术", 
     "created_at": format_datetime(base_time - timedelta(days=8)),  # 这里修复了语法错误，缺少右括号
     "tags": ["深度学习", "机器学习", "神经网络"]},
    
    {"id": 3, "content": "向量数据库可以高效存储和检索向量数据", "category": "数据库", 
     "created_at": format_datetime(base_time - timedelta(days=6)),
     "tags": ["向量数据库", "数据检索", "高效存储"]},
    
    {"id": 4, "content": "SQLite是一个轻量级的关系型数据库", "category": "数据库", 
     "created_at": format_datetime(base_time - timedelta(days=5)),
     "tags": ["SQLite", "关系型数据库", "轻量级"]},
    
    {"id": 5, "content": "Python是一种流行的编程语言", "category": "编程", 
     "created_at": format_datetime(base_time - timedelta(days=4)),
     "tags": ["Python", "编程语言", "开发"]},
    
    {"id": 6, "content": "自然语言处理是处理人类语言的技术", "category": "技术", 
     "created_at": format_datetime(base_time - timedelta(days=3)),
     "tags": ["NLP", "自然语言处理", "AI"]},
    
    {"id": 7, "content": "向量相似度搜索在推荐系统中很常用", "category": "技术", 
     "created_at": format_datetime(base_time - timedelta(days=2)),
     "tags": ["向量搜索", "推荐系统", "相似度计算"]},
    
    {"id": 8, "content": "大数据分析需要高效的数据存储和处理", "category": "数据", 
     "created_at": format_datetime(base_time - timedelta(days=1)),
     "tags": ["大数据", "数据分析", "数据处理"]}
]

# 为每个文档生成embedding向量
for doc in documents:
    embedding = model.encode(doc["content"])
    doc["embedding"] = embedding

# 展示部分数据
for doc in documents[:2]:
    print(f"ID: {doc['id']}, 内容: {doc['content']}")
    print(f"向量维度: {len(doc['embedding'])}, 向量前几个元素: {doc['embedding'][:5]}...\n")
    
    
# 这里是使用向量浮点数插入的
insert_documents(cursor,documents)


def knn_search(cursor, query_embedding, k=3, category=None, content_filter=None, start_date=None, end_date=None, tags=None):
    """执行KNN搜索，从向量表和元数据表联合查询
    
    参数:
        cursor: 数据库游标
        query_embedding: 查询向量
        k: 返回最相似的k个结果
        category: 可选，按类别精确过滤
        content_filter: 可选，按内容模糊过滤（使用LIKE语法）
        start_date: 可选，开始日期时间过滤（包含此时间）
        end_date: 可选，结束日期时间过滤（包含此时间）
        tags: 可选，按标签过滤（字符串列表，任一标签匹配即可）
    """
    query_json = json.dumps(query_embedding.tolist())
    
    # 1. 首先根据过滤条件获取符合条件的文档ID
    filter_query = """
    SELECT m.document_id
    FROM doc_metadata m
    WHERE 1=1
    """
    
    filter_params = []
    
    if category:
        filter_query += " AND m.category = ?"
        filter_params.append(category)
    
    if content_filter:
        filter_query += " AND m.original_content LIKE ?"
        filter_params.append(f"%{content_filter}%")
    
    if start_date:
        filter_query += " AND m.created_at >= ?"
        filter_params.append(start_date)
    
    if end_date:
        filter_query += " AND m.created_at <= ?"
        filter_params.append(end_date)
        
    if tags and isinstance(tags, list) and tags:
        tag_conditions = []
        for tag in tags:
            tag_conditions.append("m.tags LIKE ?")
            filter_params.append(f"%{tag}%")
        filter_query += f" AND ({' OR '.join(tag_conditions)})"
    
    # 执行过滤查询
    cursor.execute(filter_query, filter_params)
    filtered_ids = [row[0] for row in cursor.fetchall()]
    
    # 如果没有符合条件的结果，直接返回空列表
    if not filtered_ids:
        return []
    
    # 2. 创建一个临时虚拟表，只包含符合过滤条件的文档
    filtered_ids_str = ','.join(str(id) for id in filtered_ids)
    
    # 3. 在符合条件的文档中执行向量相似度搜索
    knn_query = f"""
    SELECT v.document_id, m.original_content, m.category, m.created_at, m.tags, v.distance
    FROM vec_embeddings v
    JOIN doc_metadata m ON v.document_id = m.document_id
    WHERE v.document_id IN ({filtered_ids_str})
    AND v.content_embedding MATCH ? AND k = ?
    """
    
    knn_params = [query_json, min(k, len(filtered_ids))]  # 确保k不大于过滤后的结果数
    
    # 执行向量搜索查询
    cursor.execute(knn_query, knn_params)
    
    return [(row[0], row[1], row[2], row[3], row[4], row[5]) for row in cursor.fetchall()]


# 生成查询向量
query_text = "数据库技术与应用"
query_embedding = model.encode(query_text)


# 执行KNN查询
k = 3
# 试试普通查询（不过滤）
results = knn_search(cursor, query_embedding, k)
print(f"\n查询：'{query_text}'的最近{k}个结果（不过滤）:")
for doc_id, content, category, timestamp, tags, distance in results:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

# 测试按类别过滤
category_filter = "数据库"
results_by_category = knn_search(cursor, query_embedding, k, category=category_filter)
print(f"\n查询：'{query_text}'的最近{k}个结果（按类别'{category_filter}'过滤）:")
for doc_id, content, category, timestamp, tags, distance in results_by_category:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

# 测试按内容模糊过滤
content_filter = "向量"
results_by_content = knn_search(cursor, query_embedding, k, content_filter=content_filter)
print(f"\n查询：'{query_text}'的最近{k}个结果（按内容包含'{content_filter}'过滤）:")
for doc_id, content, category, timestamp, tags, distance in results_by_content:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

# 测试组合过滤（类别+内容）
results_combined = knn_search(cursor, query_embedding, k, category="技术", content_filter="学习")
print(f"\n查询：'{query_text}'的最近{k}个结果（组合过滤：类别='技术' 且 内容包含'学习'）:")
for doc_id, content, category, timestamp, tags, distance in results_combined:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

# 测试时间过滤功能
print("\n===== 测试时间过滤功能 =====")

# 设置时间范围 - 从5天前到现在
start_date = format_datetime(base_time - timedelta(days=5))
results_by_time = knn_search(cursor, query_embedding, k, start_date=start_date)
print(f"\n查询：'{query_text}'的最近{k}个结果（时间过滤：从 {start_date} 到现在）:")
for doc_id, content, category, timestamp, tags, distance in results_by_time:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

# 设置一个更精确的时间范围
start_date = format_datetime(base_time - timedelta(days=5))
end_date = format_datetime(base_time - timedelta(days=2))
results_by_time_range = knn_search(cursor, query_embedding, k, start_date=start_date, end_date=end_date)
print(f"\n查询：'{query_text}'的最近{k}个结果（时间过滤：从 {start_date} 到 {end_date}）:")
for doc_id, content, category, timestamp, tags, distance in results_by_time_range:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

# 测试综合过滤：时间 + 类别 + 内容
start_date = format_datetime(base_time - timedelta(days=7))
results_combined = knn_search(cursor, query_embedding, k, category="数据库", content_filter="数据", start_date=start_date)
print(f"\n查询：'{query_text}'的最近{k}个结果（综合过滤：类别='数据库' 且 内容包含'数据' 且 时间>={start_date}）:")
for doc_id, content, category, timestamp, tags, distance in results_combined:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

# 测试标签过滤功能
print("\n===== 测试标签过滤功能 =====")

# 按单个标签过滤
tag_filter = ["数据库"]
results_by_tag = knn_search(cursor, query_embedding, k, tags=tag_filter)
print(f"\n查询：'{query_text}'的最近{k}个结果（按标签'{tag_filter}'过滤）:")
for doc_id, content, category, timestamp, tags, distance in results_by_tag:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

# 按多个标签过滤（OR逻辑）
tag_filter = ["AI", "数据检索"]
results_by_tags = knn_search(cursor, query_embedding, k, tags=tag_filter)
print(f"\n查询：'{query_text}'的最近{k}个结果（按标签{tag_filter}过滤，OR逻辑）:")
for doc_id, content, category, timestamp, tags, distance in results_by_tags:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

# 测试综合过滤：标签 + 类别 + 时间
tag_filter = ["数据"]
start_date = format_datetime(base_time - timedelta(days=7))
results_combined_with_tags = knn_search(cursor, query_embedding, k, category="数据库", tags=tag_filter, start_date=start_date)
print(f"\n查询：'{query_text}'的最近{k}个结果（综合过滤：类别='数据库' 且 包含标签'{tag_filter}' 且 时间>={start_date}）:")
for doc_id, content, category, timestamp, tags, distance in results_combined_with_tags:
    tags_list = json.loads(tags) if tags else []
    print(f"ID: {doc_id}, 距离: {distance:.4f}, 类别: {category}, 时间: {timestamp}, 标签: {tags_list}, 内容: {content}")

