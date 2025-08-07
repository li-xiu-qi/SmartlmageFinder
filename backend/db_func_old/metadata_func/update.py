import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, Any

def update_image_metadata(db: sqlite3.Connection, image_id: int, metadata_data: Dict[str, Any]) -> bool:
  """
  更新数据库中指定图片的元数据。
  元数据以JSON字符串的形式存储。

  参数：
    db: 数据库连接对象
    image_id: 要更新的图片ID
    metadata_data: 包含新元数据的字典。
            键必须是字符串，值可以是任何可JSON序列化的类型。
            前端当前发送的是字符串值。

  返回：
    如果更新成功（即至少影响一行）返回True，否则返回False。
  """
  try:
    # 确保所有键都是字符串，因为JSON对象的键必须是字符串
    # 值将由json.dumps处理
    validated_metadata_data = {str(k): v for k, v in metadata_data.items()}
    metadata_json = json.dumps(validated_metadata_data)
    updated_at_iso = datetime.now(timezone.utc).isoformat()
    
    cursor = db.cursor()
    cursor.execute("""
      UPDATE images
      SET metadata = ?, updated_at = ?
      WHERE id = ?
    """, (metadata_json, updated_at_iso, image_id))
    
    db.commit()
    
    # cursor.rowcount如果更新成功且行存在则为1
    # 如果未找到具有该ID的行则为0
    if cursor.rowcount > 0:
      return True
    else:
      # 这种情况意味着image_id不存在，所以没有进行更新
      # 根据需求，这可能需要记录或作为错误处理
      print(f"警告：未找到ID为{image_id}的图片，无法更新元数据。")
      return False
      
  except sqlite3.Error as e:
    print(f"更新图片ID {image_id}的元数据时发生数据库错误：{e}")
    try:
      db.rollback() # 如果事务已启动，尝试回滚
    except Exception as rb_e:
      print(f"回滚过程中发生错误：{rb_e}")
    return False
  except json.JSONEncoderError as e:
    print(f"将图片ID {image_id}的元数据编码为JSON时发生错误：{e}")
    # 这里不需要回滚，因为错误发生在数据库操作之前
    return False
  except Exception as e:
    print(f"更新图片ID {image_id}的元数据时发生意外错误：{e}")
    try:
      db.rollback() # 尝试回滚
    except Exception as rb_e:
      print(f"回滚过程中发生错误：{rb_e}")
    return False
