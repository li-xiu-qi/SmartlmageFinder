"""
数据库模块，处理所有数据库操作
"""

# 导入核心功能
from .core import (
    get_db_connection, 
    init_db, 
    dict_factory
)

# 导入图片相关功能
from .images import (
    get_image_by_uuid,
    get_images,
    create_image,
    update_image,
    delete_image,
    get_images_by_uuids
)

# 导入向量相关功能
from .vectors import (
    add_title_vector,
    add_description_vector,
    add_image_vector,
    delete_vectors,
    save_indices
)

# 导入搜索相关功能
from .search import (
    search_by_title,
    search_by_description,
    search_by_image,
    search_by_uuid,
    search_by_text,
    search_by_title_vector,
    search_by_description_vector,
    search_by_image_vector,
    title_only_search,
    description_only_search,
    simple_text_search,
    vector_text_search,
    hybrid_text_search,
    search_by_image_path,
    search_similar_to_uuid,
    search_images_by_text_fts
)

# 导入标签相关功能
from .tags import (
    get_popular_tags,
    add_tags_to_image,
    remove_tag_from_image
)

# 导入元数据相关功能
from .metadata import (
    get_metadata_fields,
    update_image_metadata
)
