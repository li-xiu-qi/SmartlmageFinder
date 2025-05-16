# SmartImageFinder 数据库设计文档

## 目录

1. [数据库概述](#数据库概述)
2. [数据库连接管理](#数据库连接管理)
3. [表结构设计](#表结构设计)
   - [images 表](#images-表)
   - [向量表](#向量表)
     - [title_vectors 表](#title_vectors-表)
     - [description_vectors 表](#description_vectors-表)
     - [image_vectors 表](#image_vectors-表)
4. [索引设计](#索引设计)
5. [关键函数](#关键函数)
6. [初始化流程](#初始化流程)
7. [向量扩展](#向量扩展)

## 数据库概述

SmartImageFinder 项目使用 SQLite 作为数据库存储引擎，同时结合向量数据库扩展(sqlite-vec)来支持图像向量检索功能。数据库主要存储图像元数据信息以及对应的向量表示，用于实现基于语义的图像检索。

数据库文件路径通过配置文件中的 `DB_PATH` 配置项指定，而向量数据库驱动程序通过 `VECTOR_DB_DRIVER` 配置项指定。

## 数据库连接管理

数据库连接采用上下文管理器模式，确保连接在使用后正确关闭，避免资源泄漏：

```python
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

def get_db():
    with get_db_connection() as conn:
        yield conn
```

这种设计模式允许开发者使用 `with` 语句安全地获取和释放数据库连接。

## 表结构设计

### images 表

`images` 表存储图像的基本信息和元数据，是系统的核心数据表。

| 字段名       | 类型    | 说明                     |
|-------------|--------|------------------------|
| id          | INTEGER| 主键，自增               |
| filename    | TEXT   | 图像文件名               |
| filepath    | TEXT   | 图像文件路径             |
| title       | TEXT   | 图像标题                 |
| description | TEXT   | 图像描述                 |
| file_size   | INTEGER| 文件大小（字节）         |
| file_type   | TEXT   | 文件类型（如jpg, png等） |
| width       | INTEGER| 图像宽度（像素）         |
| height      | INTEGER| 图像高度（像素）         |
| created_at  | TEXT   | 记录创建时间             |
| updated_at  | TEXT   | 记录更新时间             |
| metadata    | TEXT   | 额外元数据（JSON格式）   |
| tags        | TEXT   | 图像标签（JSON格式的标签数组）|

### 向量表

系统使用三个向量表存储不同类型的向量表示，这些表都是使用 sqlite-vec 扩展实现的虚拟表，支持向量相似度搜索。

#### title_vectors 表

存储图像标题对应的向量表示。

| 字段名     | 类型    | 说明                     |
|-----------|--------|------------------------|
| id        | INTEGER| 主键，自增               |
| image_id  | INTEGER| 关联到 images 表的外键，唯一 |
| embedding | FLOAT[] | 标题的向量表示，维度由配置决定 |

#### description_vectors 表

存储图像描述对应的向量表示。

| 字段名     | 类型    | 说明                     |
|-----------|--------|------------------------|
| id        | INTEGER| 主键，自增               |
| image_id  | INTEGER| 关联到 images 表的外键，唯一 |
| embedding | FLOAT[] | 描述的向量表示，维度由配置决定 |

#### image_vectors 表

存储图像内容对应的向量表示。

| 字段名     | 类型    | 说明                     |
|-----------|--------|------------------------|
| id        | INTEGER| 主键，自增               |
| image_id  | INTEGER| 关联到 images 表的外键，唯一 |
| embedding | FLOAT[] | 图像的向量表示，维度由配置决定 |

## 索引设计

为了提高查询性能，系统在 `images` 表的 `created_at` 字段上创建了索引：

```sql
CREATE INDEX IF NOT EXISTS idx_images_created_at ON images(created_at)
```

这使得按时间顺序检索图像时性能得到优化。

向量表使用 sqlite-vec 扩展提供的向量索引，支持基于余弦相似度（DISTANCE_METRIC=cosine）的高效相似度搜索。

## 关键函数

系统提供了以下关键数据库操作函数：

1. **`init_db()`**: 初始化数据库结构，包括创建表、加载向量扩展、创建索引等
2. **`get_db_connection()`**: 获取数据库连接的上下文管理器
3. **`get_db()`**: 获取数据库连接的生成器函数
4. **`dict_factory()`**: 将 sqlite3.Row 转换为字典的工具函数
5. **`format_datetime()`**: 格式化日期时间
6. **`get_current_time()`**: 获取当前时间的标准格式字符串

## 初始化流程

数据库初始化流程包括以下步骤：

1. 创建数据库连接
2. 加载 sqlite-vec 向量扩展
3. 获取配置的向量维度
4. 创建 images 表
5. 创建三个向量表（title_vectors, description_vectors, image_vectors）
6. 创建必要的索引
7. 提交事务

## 向量扩展

系统依赖 sqlite-vec 扩展提供向量存储和检索功能。该扩展允许：

1. 存储高维向量数据
2. 执行基于余弦相似度的向量检索
3. 高效地进行最近邻搜索

向量维度通过 `get_embedding_dimension()` 函数从配置或模型中获取，确保向量表的维度与实际使用的嵌入模型匹配。

在初始化数据库时，系统会尝试加载向量扩展，如果加载失败，将无法使用向量相关功能，但基本的图像元数据存储功能不受影响。
