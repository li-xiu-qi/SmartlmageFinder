#!/usr/bin/env python3
"""
测试元数据更新功能
"""

import sqlite3
import json
from backend.config import settings
from backend.db_func.core import get_db_connection
from backend.db_func.metadata_func.update import update_image_metadata
from backend.db_func.images_func.get import get_image_by_id

def test_metadata_update():
    """测试元数据更新功能"""
    print("开始测试元数据更新功能...")
    try:
        print("尝试获取数据库连接...")
        # 获取数据库连接
        with get_db_connection() as conn:
            print("数据库连接成功!")
            # 首先获取第一张图片
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM images LIMIT 1")
            result = cursor.fetchone()
            
            if not result:
                print("数据库中没有图片记录")
                return
                
            image_id = result[0]
            print(f"找到图片ID: {image_id}")
            
            # 获取图片信息
            image_info = get_image_by_id(conn, image_id)
            print(f"图片信息: {image_info}")
            
            # 测试元数据更新
            test_metadata = {
                "test_key": "test_value",
                "camera": "Canon EOS R5",
                "iso": "400"
            }
            
            print(f"尝试更新元数据: {test_metadata}")
            success = update_image_metadata(conn, image_id, test_metadata)
            
            if success:
                print("元数据更新成功!")
                # 验证更新结果
                updated_image = get_image_by_id(conn, image_id)
                print(f"更新后的图片信息: {updated_image}")
            else:
                print("元数据更新失败!")
                
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metadata_update()
