#!/usr/bin/env python3
"""
测试批量向量生成性能脚本
对比逐个处理 vs 批量处理的性能差异
"""

import time
import sqlite3
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.generate_vector import encode_text, encode_image
from backend.db_func.vector_func.batch_vectors import BatchVectorManager
from backend.db_func.vector_func.add_image_vectors import add_image_vector
from backend.db_func.vector_func.add_text_vectors import add_title_vector, add_description_vector


def test_text_encoding_performance():
    """测试文本编码性能对比"""
    print("=" * 50)
    print("测试文本编码性能")
    print("=" * 50)
    
    # 测试数据
    texts = [
        "美丽的日出风景照片",
        "城市夜景高楼大厦",
        "自然风光山水画",
        "人物肖像摄影作品",
        "抽象艺术设计图案",
        "动物野生动物园",
        "花卉植物园林",
        "建筑历史古迹",
        "科技产品展示",
        "美食料理烹饪"
    ] * 10  # 100个文本
    
    print(f"测试数据量: {len(texts)} 个文本")
    
    # 逐个处理
    start_time = time.time()
    individual_vectors = []
    for text in texts:
        vector = encode_text(text)
        individual_vectors.append(vector)
    individual_time = time.time() - start_time
    
    # 批量处理
    start_time = time.time()
    batch_vectors = encode_text(texts)
    batch_time = time.time() - start_time
    
    print(f"逐个处理时间: {individual_time:.3f} 秒")
    print(f"批量处理时间: {batch_time:.3f} 秒")
    print(f"性能提升: {individual_time / batch_time:.1f}x")
    print(f"向量维度: {individual_vectors[0].shape[0]}")
    print()


def test_image_encoding_performance():
    """测试图像编码性能对比"""
    print("=" * 50)
    print("测试图像编码性能")
    print("=" * 50)
    
    # 查找测试图片
    image_dir = project_root / "data" / "images"
    if not image_dir.exists():
        print("图片目录不存在，跳过图像编码测试")
        return
    
    image_files = list(image_dir.glob("*.png"))[:10]  # 取前10张图片
    if not image_files:
        print("没有找到测试图片，跳过图像编码测试")
        return
    
    image_paths = [str(img) for img in image_files]
    print(f"测试数据量: {len(image_paths)} 张图片")
    
    # 逐个处理
    start_time = time.time()
    individual_vectors = []
    for path in image_paths:
        vector = encode_image(path)
        individual_vectors.append(vector)
    individual_time = time.time() - start_time
    
    # 批量处理
    start_time = time.time()
    batch_vectors = encode_image(image_paths)
    batch_time = time.time() - start_time
    
    print(f"逐个处理时间: {individual_time:.3f} 秒")
    print(f"批量处理时间: {batch_time:.3f} 秒")
    print(f"性能提升: {individual_time / batch_time:.1f}x")
    print(f"向量维度: {individual_vectors[0].shape[0]}")
    print()


def test_database_batch_processing():
    """测试数据库批量处理性能"""
    print("=" * 50)
    print("测试数据库批量处理性能")
    print("=" * 50)
    
    # 创建临时数据库
    test_db_path = project_root / "backend" / "tests" / "test_batch_performance.db"
    conn = sqlite3.connect(str(test_db_path))
    
    try:
        # 创建测试表
        setup_test_database(conn)
        
        # 准备测试数据
        test_data = []
        for i in range(20):
            test_data.append({
                'image_id': i + 1,
                'filepath': f"/fake/path/image_{i+1}.jpg",
                'title': f"测试图片标题 {i+1}",
                'description': f"这是第 {i+1} 张测试图片的详细描述"
            })
        
        print(f"测试数据量: {len(test_data)} 条记录")
        
        # 插入基础数据
        cursor = conn.cursor()
        for data in test_data:
            cursor.execute(
                "INSERT INTO images (id, filename) VALUES (?, ?)",
                (data['image_id'], f"image_{data['image_id']}.jpg")
            )
        conn.commit()
        
        # 测试逐个处理
        start_time = time.time()
        for data in test_data:
            # 模拟逐个生成向量 (跳过实际文件处理)
            fake_vector = [0.1] * 1024
            vector_json = json.dumps(fake_vector)
            
            # 插入向量数据
            cursor.execute(
                "INSERT OR REPLACE INTO title_vectors(image_id, embedding) VALUES (?, ?)",
                (data['image_id'], vector_json)
            )
            cursor.execute(
                "INSERT OR REPLACE INTO description_vectors(image_id, embedding) VALUES (?, ?)",
                (data['image_id'], vector_json)
            )
        conn.commit()
        individual_time = time.time() - start_time
        
        # 清理数据
        cursor.execute("DELETE FROM title_vectors")
        cursor.execute("DELETE FROM description_vectors")
        conn.commit()
        
        # 测试批量处理
        start_time = time.time()
        
        # 批量准备数据
        title_batch = []
        desc_batch = []
        for data in test_data:
            fake_vector = [0.1] * 1024
            vector_json = json.dumps(fake_vector)
            title_batch.append((data['image_id'], vector_json))
            desc_batch.append((data['image_id'], vector_json))
        
        # 批量插入
        cursor.executemany(
            "INSERT OR REPLACE INTO title_vectors(image_id, embedding) VALUES (?, ?)",
            title_batch
        )
        cursor.executemany(
            "INSERT OR REPLACE INTO description_vectors(image_id, embedding) VALUES (?, ?)",
            desc_batch
        )
        conn.commit()
        batch_time = time.time() - start_time
        
        print(f"逐个处理时间: {individual_time:.3f} 秒")
        print(f"批量处理时间: {batch_time:.3f} 秒")
        print(f"性能提升: {individual_time / batch_time:.1f}x")
        print()
        
    finally:
        conn.close()
        # 清理测试文件
        if test_db_path.exists():
            test_db_path.unlink()


def setup_test_database(conn):
    """设置测试数据库"""
    cursor = conn.cursor()
    
    # 创建测试表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            filename TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS title_vectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER,
            embedding TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS description_vectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_id INTEGER,
            embedding TEXT
        )
    """)
    
    conn.commit()


def main():
    """主测试函数"""
    print("批量向量生成性能测试")
    print("=" * 50)
    
    # 测试文本编码
    test_text_encoding_performance()
    
    # 测试图像编码  
    test_image_encoding_performance()
    
    # 测试数据库批量处理
    test_database_batch_processing()
    
    print("=" * 50)
    print("测试完成！")


if __name__ == "__main__":
    import json
    main()
