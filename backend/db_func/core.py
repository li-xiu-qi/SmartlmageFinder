"""
数据库核心功能模块，包含数据库连接和初始化
"""
import sqlite3
import json
import traceback
from typing import Dict, Any, List
import os
from datetime import datetime
from contextlib import contextmanager

# 导入配置
from ..config import settings
from ..utils.generate_vector import get_embedding_dimension

def format_datetime(dt):
    """将datetime对象格式化为标准格式字符串"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def get_current_time():
    """获取当前时间，格式化为标准格式"""
    return format_datetime(datetime.now())

@contextmanager
def get_db_connection():
    """获取数据库连接，使用上下文管理器确保连接正确关闭"""
    conn = None
    try:
        conn = sqlite3.connect(settings.get_config().DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            conn.close()

def init_db():
    """初始化数据库表结构"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 加载向量扩展
        try:
            conn.enable_load_extension(True)
            conn.execute(f"SELECT load_extension('{settings.get_config().VECTOR_DB_DRIVER}')")
            cursor.execute("SELECT vec_version()")
            version = cursor.fetchone()[0]
            print(f"成功加载sqlite-vec扩展，版本: {version}")
        except Exception as e:
            print(f"加载sqlite-vec扩展失败: {e}")
            print("无法使用向量功能，请确保扩展文件存在并可访问")
            print(f"扩展文件路径: {settings.get_config().VECTOR_DB_DRIVER}")
        
        # 获取向量维度
        embedding_dim = get_embedding_dimension()
        
        # 创建图片表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            title TEXT,
            description TEXT,
            file_size INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            width INTEGER,
            height INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata TEXT,
            tags TEXT
        )
        ''')
        
        # 创建向量表，使用image_id替代uuid
        try:
            cursor.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS title_vectors USING vec0(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER UNIQUE NOT NULL,
                embedding FLOAT[{embedding_dim}] DISTANCE_METRIC=cosine
            );
            """)
            
            cursor.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS description_vectors USING vec0(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER UNIQUE NOT NULL,
                embedding FLOAT[{embedding_dim}] DISTANCE_METRIC=cosine
            );
            """)
            
            cursor.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS image_vectors USING vec0(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER UNIQUE NOT NULL,
                embedding FLOAT[{embedding_dim}] DISTANCE_METRIC=cosine
            );
            """)
            
            print(f"创建向量表成功，向量维度: {embedding_dim}")
        except Exception as e:
            print(f"创建向量表失败: {e}")
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at)')
        
        conn.commit()
    
    print("数据库初始化完成")

def dict_factory(cursor, row):
    """将sqlite3.Row转换为dict"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
