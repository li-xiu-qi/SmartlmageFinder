import json
from typing import Dict, List, Any, Optional

def row_to_dict(row):
    """将 sqlite3.Row 对象转换为字典"""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()} if hasattr(row, 'keys') else dict(row)


def rows_to_dicts(rows):
    """将 sqlite3.Row 对象列表转换为字典列表"""
    return [row_to_dict(row) for row in rows] if rows else []


def json_from_db_to_python(image: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """处理图片记录中的JSON字段，将数据库中存储的JSON字符串转换为Python对象
    
    这个函数用于从数据库读取图片记录后的数据处理，主要解析tags和metadata字段，
    将它们从JSON字符串转换为Python数据结构（列表和字典）。
    
    Args:
        image: 包含图片信息的字典，通常是从数据库查询得到的一条记录
               例如: {'id': 1, 'tags': '["nature", "sunset"]', 'metadata': '{"location": "beach"}'}
    
    Returns:
        处理后的同一字典，其中JSON字段已被解析为Python对象
        例如: {'id': 1, 'tags': ['nature', 'sunset'], 'metadata': {'location': 'beach']}
        如果输入为None或空，则返回None
    """
    if not image:
        return None
        
    # 处理标签字段
    if image.get('tags'):
        try:
            image['tags'] = json.loads(image['tags'])
        except:
            image['tags'] = []
    else:
        image['tags'] = []
        
    # 处理元数据字段
    if image.get('metadata'):
        try:
            image['metadata'] = json.loads(image['metadata'])
        except:
            image['metadata'] = {}
    else:
        image['metadata'] = {}
        
    return image

def python_to_json_for_db(data: Any, default_value: Any) -> str:
    """将Python对象转换为JSON字符串以便存储到数据库
    
    这个函数在向数据库写入数据前调用，确保数据以正确的JSON格式存储，
    并处理空值情况，提供默认值。
    
    Args:
        data: 要转换为JSON的Python数据（可以是字典、列表等任何可序列化对象）
              例如: ['tag1', 'tag2'] 或 {'key': 'value'}
        default_value: 当data为None或空时使用的默认值
                      例如: [] 用于tags字段，{} 用于metadata字段
    
    Returns:
        编码后的JSON字符串，确保非ASCII字符被正确处理
        例如: '["tag1", "tag2"]' 或 '{"key": "value"}'
    """
    if data:
        return json.dumps(data, ensure_ascii=False)
    return json.dumps(default_value, ensure_ascii=False)
