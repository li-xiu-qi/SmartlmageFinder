"""
演示WAL模式对并发性能的影响
"""
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor

def test_database_mode(db_path, wal_mode=True):
    """测试数据库模式的并发性能"""
    
    # 创建测试数据库
    conn = sqlite3.connect(db_path)
    
    # 设置模式
    if wal_mode:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        print("✓ 启用WAL模式")
    else:
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("PRAGMA synchronous=FULL")
        print("✓ 使用传统模式")
    
    # 创建测试表
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_images (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    
    # 测试函数
    def write_operation(thread_id):
        """模拟写操作（上传图片）"""
        conn = sqlite3.connect(db_path)
        start_time = time.time()
        
        for i in range(10):
            conn.execute(
                "INSERT INTO test_images (filename, data) VALUES (?, ?)",
                (f"thread_{thread_id}_image_{i}.jpg", f"data_{thread_id}_{i}")
            )
            conn.commit()
            time.sleep(0.01)  # 模拟向量生成时间
        
        conn.close()
        end_time = time.time()
        return f"写线程{thread_id}: {end_time - start_time:.2f}秒"
    
    def read_operation(thread_id):
        """模拟读操作（搜索图片）"""
        conn = sqlite3.connect(db_path)
        start_time = time.time()
        
        for i in range(20):
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_images")
            count = cursor.fetchone()[0]
            time.sleep(0.005)  # 模拟搜索处理时间
        
        conn.close()
        end_time = time.time()
        return f"读线程{thread_id}: {end_time - start_time:.2f}秒, 最终记录数: {count}"
    
    # 并发测试
    print(f"\n开始并发测试...")
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        # 提交写任务
        write_futures = [executor.submit(write_operation, i) for i in range(2)]
        # 提交读任务
        read_futures = [executor.submit(read_operation, i) for i in range(4)]
        
        # 收集结果
        results = []
        for future in write_futures + read_futures:
            results.append(future.result())
    
    total_time = time.time() - start_time
    
    print(f"总执行时间: {total_time:.2f}秒")
    for result in results:
        print(f"  {result}")
    
    return total_time

if __name__ == "__main__":
    print("=== WAL模式性能测试 ===")
    
    # 测试传统模式
    print("\n1. 传统模式测试:")
    traditional_time = test_database_mode("test_traditional.db", wal_mode=False)
    
    # 测试WAL模式
    print("\n2. WAL模式测试:")
    wal_time = test_database_mode("test_wal.db", wal_mode=True)
    
    # 性能对比
    improvement = (traditional_time - wal_time) / traditional_time * 100
    print(f"\n=== 性能对比 ===")
    print(f"传统模式: {traditional_time:.2f}秒")
    print(f"WAL模式:  {wal_time:.2f}秒")
    print(f"性能提升: {improvement:.1f}%")
    
    # 清理测试文件
    import os
    for file in ["test_traditional.db", "test_wal.db", "test_wal.db-wal", "test_wal.db-shm"]:
        try:
            os.remove(file)
        except:
            pass
