"""
数据库核心功能模块，包含数据库连接和初始化
"""
import sqlite3
from contextlib import contextmanager

from .connection import get_db_connection_from_pool, get_db_connection
from ...config import settings
from ...ai_func.generate_vector import get_embedding_dimension


def get_db():
    """
    FastAPI 依赖项，用于获取数据库连接
    优先使用连接池，如果连接池未初始化则使用单连接模式
    """
    try:
        # 尝试从连接池获取连接
        with get_db_connection_from_pool() as conn:
            yield conn
    except RuntimeError:
        # 连接池未初始化，使用单连接模式
        with get_db_connection() as conn:
            yield conn


def init_db():
    """初始化数据库表结构"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 加载向量扩展
        try:
            conn.enable_load_extension(True)
            conn.execute(f"SELECT load_extension('{settings.get_config().VECTOR_DB_DRIVER}')")
            cursor.execute("SELECT vec_version()")
            result = cursor.fetchone()
            version = result[0] if result else "未知"
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
