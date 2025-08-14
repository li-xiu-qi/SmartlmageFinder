"""
数据库初始化模块

仅负责 init_db：创建表 / 虚表 / 索引。
运行期获取连接统一使用 core.connection.get_db。
"""
import sqlite3

from .connection import get_db_connection
from ...config import settings
from ...ai_func.generate_vector import get_embedding_dimension
from .extensions.loader import setup_connection, verify_vector_extension

_INIT_DONE = False


def init_db():
    """初始化数据库表结构"""
    global _INIT_DONE
    if _INIT_DONE:
        print("init_db 已执行，跳过")
        return

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 统一通过扩展加载器加载 (幂等)
        success = setup_connection(conn, silent=False)
        if not success:
            print("致命错误: 向量扩展加载失败，程序退出")
            raise SystemExit(1)
        ok, ver = verify_vector_extension(conn)
        if ok:
            print(f"向量扩展验证成功: {ver}")
        else:
            print(f"致命错误: 向量扩展验证失败: {ver}")
            raise SystemExit(1)
        
        # 优化并发读：启用 WAL 日志模式与合适的同步级别（幂等设置）
        try:
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            print("已设置 PRAGMA journal_mode=WAL, synchronous=NORMAL")
        except Exception as e:
            # PRAGMA 失败不影响主流程（例如某些环境不支持 WAL）
            print(f"设置 WAL 失败: {e}")
        
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

        # 修复：若存在历史迁移遗留的 vec0 影子表名（如 image_vectors_new_chunks），统一重命名回标准名
        # 目标：{base}_new_* -> {base}_*
        try:
            for base in ("title_vectors", "description_vectors", "image_vectors"):
                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE ?",
                    (f"{base}_new_%",),
                )
                rows = cursor.fetchall()
                for r in rows:
                    old_name = r[0] if not isinstance(r, sqlite3.Row) else r["name"]
                    prefix = f"{base}_new_"
                    if old_name.startswith(prefix):
                        tail = old_name[len(prefix):]
                        new_name = f"{base}_{tail}"
                        try:
                            cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
                            print(f"修复影子表: {old_name} -> {new_name}")
                        except Exception:
                            # 若重命名失败（目标已存在或非影子表），跳过
                            pass
        except Exception:
            # 修复逻辑失败不影响主流程
            pass
        
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
        
        # 模型迁移记录表（离线向量重建与模型更换时使用）
        cursor.execute('''
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
            last_image_id INTEGER,            -- 新增: 已处理的最后一个 images.id, 便于断点续传
            note TEXT
        )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_migrations_status ON model_migrations(status)')
        # 兼容老版本添加 last_image_id 列
        try:
            cursor.execute("PRAGMA table_info(model_migrations)")
            cols = [r[1] for r in cursor.fetchall()]
            if 'last_image_id' not in cols:
                cursor.execute('ALTER TABLE model_migrations ADD COLUMN last_image_id INTEGER')
        except Exception:
            pass
        
        conn.commit()
    
    _INIT_DONE = True
    print("数据库初始化完成")
