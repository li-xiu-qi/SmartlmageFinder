"""
数据库初始化模块

仅负责 init_db：创建表 / 虚表 / 索引。
运行期获取连接统一使用 core.connection.get_db。
"""
import sqlite3

from .connection import get_db_connection
from ...config import settings
from ...ai_func.generate_vector import get_embedding_dimension


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

        # 请求会话记录表，用于前后端以请求ID维护会话
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS request_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL UNIQUE,
            conversation_id TEXT NOT NULL,
            user_id TEXT,
            endpoint TEXT NOT NULL,
            messages TEXT,
            state TEXT,
            vector_targets TEXT,
            filters TEXT,
            selected_ids TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            error TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_request_sessions_conv ON request_sessions(conversation_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_request_sessions_created ON request_sessions(created_at)')

        # 对话消息表（精简化，仅存消息文本与引用的图片ID列表）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT,
            image_ids TEXT,
            metadata TEXT,
            created_at TEXT NOT NULL
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conv_messages_conv_created ON conversation_messages(conversation_id, created_at)')
        
        conn.commit()
    
    print("数据库初始化完成")
