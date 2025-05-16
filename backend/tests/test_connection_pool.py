"""
测试SQLite连接池的性能和稳定性，包括同步和异步实现
"""
import os
import sys
import time
import threading
import sqlite3
from concurrent.futures import ThreadPoolExecutor
import statistics
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import queue
import asyncio
import aiosqlite  # 需要安装: pip install aiosqlite
from contextlib import contextmanager, asynccontextmanager
import numpy as np

plt.rcParams['font.family'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


# 测试数据库路径
TEST_DB_PATH = os.path.join("./test_db.db")

# 在测试文件中直接实现连接池
class DBConnectionPool:
    """SQLite数据库连接池，优化读写锁实现"""
    _instance = None
    _instance_lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super(DBConnectionPool, cls).__new__(cls)
            return cls._instance
    
    def __init__(self, db_path=None, max_connections=10, timeout=5):
        if not hasattr(self, 'initialized'):
            self.db_path = db_path or TEST_DB_PATH
            self.max_connections = max_connections
            self.timeout = timeout
            self.pool = queue.Queue(maxsize=max_connections)
            self.active_connections = 0
            self.write_lock = threading.Lock()  # 只在修改连接池状态时使用
            self.initialized = True
            
            # 预创建一些连接
            self._init_connections(min(3, max_connections))
    
    def _init_connections(self, num):
        """初始化一定数量的连接"""
        for _ in range(num):
            conn = self._create_connection()
            if conn:
                self.pool.put(conn)
    
    def _create_connection(self):
        """创建新的数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            print(f"创建数据库连接失败: {e}")
            return None
    
    def get_connection(self):
        """从连接池获取一个连接，如果池为空且未达到最大连接数则创建新连接"""
        try:
            # 尝试从池中获取连接 - 读操作，不需要加锁
            conn = self.pool.get(block=True, timeout=self.timeout)
            return conn
        except queue.Empty:
            # 如果池为空，检查是否可以创建新连接 - 写操作，需要加锁
            with self.write_lock:
                if self.active_connections < self.max_connections:
                    self.active_connections += 1
                    conn = self._create_connection()
                    if conn:
                        return conn
                    else:
                        self.active_connections -= 1
            
            # 如果无法创建新连接，再次尝试从池中获取
            return self.pool.get(block=True, timeout=self.timeout)
    
    def release_connection(self, conn):
        """将连接释放回连接池"""
        if conn:
            try:
                # 简单测试连接是否有效
                conn.execute("SELECT 1").fetchone()
                # 将连接放回池中 - 不需要加锁，队列内部是线程安全的
                self.pool.put(conn)
            except (sqlite3.Error, Exception) as e:
                # 连接已损坏，创建新连接替代它 - 写操作，需要加锁
                print(f"检测到损坏的连接: {e}, 创建新连接")
                with self.write_lock:
                    try:
                        conn.close()
                    except:
                        pass
                    
                    new_conn = self._create_connection()
                    if new_conn:
                        self.pool.put(new_conn)
                    else:
                        self.active_connections -= 1
    
    def close_all(self):
        """关闭所有连接"""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except:
                pass
        
        self.active_connections = 0

# 异步连接池实现
class AsyncDBConnectionPool:
    """SQLite数据库异步连接池，优化读写锁实现"""
    _instance = None
    _instance_lock = asyncio.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncDBConnectionPool, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_path=None, max_connections=10, timeout=5):
        # 普通的同步初始化
        if not hasattr(self, 'initialized'):
            self.db_path = db_path or TEST_DB_PATH
            self.max_connections = max_connections
            self.timeout = timeout
            self.pool = asyncio.Queue(maxsize=max_connections)
            self.active_connections = 0
            self.write_lock = asyncio.Lock()  # 只在修改连接池状态时使用
            self.initialized = False  # 设置为False，等待异步初始化
    
    async def initialize(self):
        """异步初始化连接池"""
        if not self.initialized:
            # 预创建一些连接
            await self._init_connections(min(3, self.max_connections))
            self.initialized = True
    
    async def _init_connections(self, num):
        """初始化一定数量的连接"""
        for _ in range(num):
            conn = await self._create_connection()
            if conn:
                await self.pool.put(conn)
    
    async def _create_connection(self):
        """创建新的数据库连接"""
        try:
            conn = await aiosqlite.connect(self.db_path)
            return conn
        except Exception as e:
            print(f"创建异步数据库连接失败: {e}")
            return None
    
    async def get_connection(self):
        """从连接池获取一个连接"""
        try:
            # 尝试从池中获取连接 - 读操作，不需要加锁
            conn = await asyncio.wait_for(self.pool.get(), self.timeout)
            return conn
        except asyncio.TimeoutError:
            # 如果超时，检查是否可以创建新连接 - 写操作，需要加锁
            async with self.write_lock:
                if self.active_connections < self.max_connections:
                    self.active_connections += 1
                    conn = await self._create_connection()
                    if conn:
                        return conn
                    else:
                        self.active_connections -= 1
            
            # 如果无法创建新连接，再次尝试从池中获取
            conn = await asyncio.wait_for(self.pool.get(), self.timeout)
            return conn
    
    async def release_connection(self, conn):
        """将连接释放回连接池"""
        if conn:
            try:
                # 简单测试连接是否有效
                async with conn.execute("SELECT 1") as cursor:
                    await cursor.fetchone()
                # 将连接放回池中 - 不需要加锁，队列内部是线程安全的
                await self.pool.put(conn)
            except Exception as e:
                # 连接已损坏，创建新连接替代它 - 写操作，需要加锁
                print(f"检测到损坏的异步连接: {e}, 创建新连接")
                async with self.write_lock:
                    try:
                        await conn.close()
                    except:
                        pass
                    
                    new_conn = await self._create_connection()
                    if new_conn:
                        await self.pool.put(new_conn)
                    else:
                        self.active_connections -= 1
    
    async def close_all(self):
        """关闭所有连接"""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                await conn.close()
            except:
                pass
        
        self.active_connections = 0

# 全局连接池实例
_connection_pool = None

def get_connection_pool(init=False):
    """获取数据库连接池单例"""
    global _connection_pool
    if _connection_pool is None or init:
        _connection_pool = DBConnectionPool()
    return _connection_pool

def init_test_db():
    """初始化测试数据库"""
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    
    # 创建测试表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_table (
        id INTEGER PRIMARY KEY,
        name TEXT,
        value INTEGER
    )
    """)
    
    # 清空测试表
    cursor.execute("DELETE FROM test_table")
    
    # 插入一些测试数据
    for i in range(1000):
        cursor.execute(f"INSERT INTO test_table VALUES ({i}, 'item_{i}', {i*10})")
    
    conn.commit()
    conn.close()

async def init_test_db_async():
    """异步初始化测试数据库"""
    async with aiosqlite.connect(TEST_DB_PATH) as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS test_table_async (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value INTEGER
        )
        """)
        
        # 清空测试表
        await conn.execute("DELETE FROM test_table_async")
        
        # 使用executemany批量插入数据
        data = [(i, f'item_{i}', i*10) for i in range(1000)]
        await conn.executemany(
            "INSERT INTO test_table_async VALUES (?, ?, ?)", data
        )
        
        await conn.commit()

def test_without_pool(num_queries, num_threads):
    """测试不使用连接池的查询性能"""
    def worker(_=None):  # 添加默认参数，解决map传参问题
        times = []
        for _ in range(num_queries // num_threads):
            start = time.time()
            conn = sqlite3.connect(TEST_DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_table ORDER BY RANDOM() LIMIT 10")
            results = cursor.fetchall()
            conn.close()
            times.append(time.time() - start)
        return times
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(worker, [None] * num_threads))
    
    all_times = [time for thread_times in results for time in thread_times]
    return all_times

def test_with_pool(num_queries, num_threads):
    """测试使用连接池的查询性能"""
    # 初始化连接池
    pool = DBConnectionPool(db_path=TEST_DB_PATH, max_connections=num_threads+2)
    
    def worker(_=None):  # 添加默认参数，解决map传参问题
        times = []
        for _ in range(num_queries // num_threads):
            start = time.time()
            conn = pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_table ORDER BY RANDOM() LIMIT 10")
            results = cursor.fetchall()
            pool.release_connection(conn)
            times.append(time.time() - start)
        return times
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(worker, [None] * num_threads))
    
    pool.close_all()
    all_times = [time for thread_times in results for time in thread_times]
    return all_times

async def test_without_pool_async(num_queries, num_concurrency):
    """测试不使用异步连接池的查询性能"""
    async def worker():
        times = []
        for _ in range(num_queries // num_concurrency):
            start = time.time()
            async with aiosqlite.connect(TEST_DB_PATH) as conn:
                async with conn.execute("SELECT * FROM test_table_async ORDER BY RANDOM() LIMIT 10") as cursor:
                    results = await cursor.fetchall()
            times.append(time.time() - start)
        return times
    
    # 创建并运行协程任务
    tasks = [worker() for _ in range(num_concurrency)]
    results = await asyncio.gather(*tasks)
    
    all_times = [time for task_times in results for time in task_times]
    return all_times

async def test_with_pool_async(num_queries, num_concurrency):
    """测试使用异步连接池的查询性能"""
    # 初始化连接池
    pool = AsyncDBConnectionPool(db_path=TEST_DB_PATH, max_connections=num_concurrency+2)
    await pool.initialize()  # 使用异步初始化方法
    
    async def worker():
        times = []
        for _ in range(num_queries // num_concurrency):
            start = time.time()
            conn = await pool.get_connection()
            async with conn.execute("SELECT * FROM test_table_async ORDER BY RANDOM() LIMIT 10") as cursor:
                results = await cursor.fetchall()
            await pool.release_connection(conn)
            times.append(time.time() - start)
        return times
    
    # 创建并运行协程任务
    tasks = [worker() for _ in range(num_concurrency)]
    results = await asyncio.gather(*tasks)
    
    await pool.close_all()
    all_times = [time for task_times in results for time in task_times]
    return all_times

def print_stats(times, label):
    """打印性能统计信息"""
    print(f"\n---- {label} ----")
    print(f"总查询数: {len(times)}")
    print(f"总执行时间: {sum(times):.4f}秒")
    print(f"平均查询时间: {sum(times) / len(times):.4f}秒")
    print(f"最小查询时间: {min(times):.4f}秒")
    print(f"最大查询时间: {max(times):.4f}秒")
    print(f"中位数查询时间: {statistics.median(times):.4f}秒")
    if len(times) > 1:
        print(f"标准差: {statistics.stdev(times):.4f}秒")

def visualize_comparison(thread_counts, no_pool_avgs, pool_avgs, improvements):
    """
    可视化性能对比
    """
    plt.figure(figsize=(15, 10))
    
    # 创建子图1：平均查询时间对比
    plt.subplot(2, 1, 1)
    plt.plot(thread_counts, no_pool_avgs, 'o-', label='不使用连接池', color='#FF5733')
    plt.plot(thread_counts, pool_avgs, 's-', label='使用连接池', color='#33A8FF')
    plt.title('不同线程数下的平均查询时间对比')
    plt.xlabel('线程数')
    plt.ylabel('平均查询时间 (秒)')
    plt.legend()
    plt.grid(True)
    
    # 创建子图2：性能提升百分比
    plt.subplot(2, 1, 2)
    bars = plt.bar(thread_counts, improvements, color='#4CAF50', alpha=0.8)
    plt.title('连接池性能提升百分比')
    plt.xlabel('线程数')
    plt.ylabel('性能提升 (%)')
    plt.grid(True, axis='y')
    
    # 在柱状图上添加具体数值
    for bar, improvement in zip(bars, improvements):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                 f'{improvement:.2f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('connection_pool_performance.png', dpi=300)
    print("\n性能对比图已保存为: connection_pool_performance.png")
    plt.show()

def visualize_all_comparison(thread_counts, 
                           sync_no_pool_avgs, sync_single_conn_avgs, sync_pool_avgs, 
                           sync_no_pool_improvements, sync_pool_improvements,
                           concurrency_levels, 
                           async_no_pool_avgs, async_single_conn_avgs, async_pool_avgs,
                           async_no_pool_improvements, async_pool_improvements):
    """
    可视化同步和异步性能对比，包含单次连接模式
    """
    plt.figure(figsize=(15, 20))
    
    # 创建子图1：同步查询时间对比
    plt.subplot(4, 1, 1)
    plt.plot(thread_counts, sync_no_pool_avgs, 'o-', label='不使用连接池', color='#FF5733')
    plt.plot(thread_counts, sync_single_conn_avgs, 's-', label='上下文管理器单次连接', color='#33FF57')
    plt.plot(thread_counts, sync_pool_avgs, '^-', label='使用连接池', color='#33A8FF')
    plt.title('同步：不同线程数下的平均查询时间')
    plt.xlabel('线程数')
    plt.ylabel('平均查询时间 (秒)')
    plt.legend()
    plt.grid(True)
    
    # 创建子图2：同步性能提升百分比
    plt.subplot(4, 1, 2)
    x = np.arange(len(thread_counts))
    width = 0.35
    bars1 = plt.bar(x - width/2, sync_no_pool_improvements, width, label='单次连接vs直接连接', color='#33FF57', alpha=0.8)
    bars2 = plt.bar(x + width/2, sync_pool_improvements, width, label='连接池vs直接连接', color='#4CAF50', alpha=0.8)
    plt.title('同步：性能提升百分比')
    plt.xlabel('线程数')
    plt.ylabel('性能提升 (%)')
    plt.xticks(x, thread_counts)
    plt.legend()
    plt.grid(True, axis='y')
    
    # 在柱状图上添加具体数值
    for bars in [bars1, bars2]:
        for bar, improvement in zip(bars, sync_no_pool_improvements if bars is bars1 else sync_pool_improvements):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{improvement:.2f}%', ha='center', va='bottom')
    
    # 创建子图3：异步查询时间对比
    plt.subplot(4, 1, 3)
    plt.plot(concurrency_levels, async_no_pool_avgs, 'o-', label='不使用连接池', color='#FF5733')
    plt.plot(concurrency_levels, async_single_conn_avgs, 's-', label='上下文管理器单次连接', color='#33FF57')
    plt.plot(concurrency_levels, async_pool_avgs, '^-', label='使用连接池', color='#33A8FF')
    plt.title('异步：不同并发级别下的平均查询时间')
    plt.xlabel('并发任务数')
    plt.ylabel('平均查询时间 (秒)')
    plt.legend()
    plt.grid(True)
    
    # 创建子图4：异步性能提升百分比
    plt.subplot(4, 1, 4)
    x = np.arange(len(concurrency_levels))
    bars1 = plt.bar(x - width/2, async_no_pool_improvements, width, label='单次连接vs直接连接', color='#33FF57', alpha=0.8)
    bars2 = plt.bar(x + width/2, async_pool_improvements, width, label='连接池vs直接连接', color='#9C27B0', alpha=0.8)
    plt.title('异步：性能提升百分比')
    plt.xlabel('并发任务数')
    plt.ylabel('性能提升 (%)')
    plt.xticks(x, concurrency_levels)
    plt.legend()
    plt.grid(True, axis='y')
    
    # 在柱状图上添加具体数值
    for bars in [bars1, bars2]:
        for bar, improvement in zip(bars, async_no_pool_improvements if bars is bars1 else async_pool_improvements):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{improvement:.2f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('connection_pool_all_comparison.png', dpi=300)
    print("\n完整性能对比图已保存为: connection_pool_all_comparison.png")
    plt.show()

# 添加单次连接的上下文管理器
@contextmanager
def get_single_connection():
    """获取单次数据库连接，使用上下文管理器确保连接正确关闭"""
    conn = None
    try:
        conn = sqlite3.connect(TEST_DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    finally:
        if conn:
            conn.close()

# 异步版本的单次连接上下文管理器
@asynccontextmanager
async def get_single_connection_async():
    """获取单次异步数据库连接，使用异步上下文管理器确保连接正确关闭"""
    conn = None
    try:
        conn = await aiosqlite.connect(TEST_DB_PATH)
        yield conn
    finally:
        if conn:
            await conn.close()

# 测试单次连接的性能
def test_with_single_connection(num_queries, num_threads):
    """测试使用单次连接的查询性能"""
    def worker(_=None):
        times = []
        for _ in range(num_queries // num_threads):
            start = time.time()
            with get_single_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM test_table ORDER BY RANDOM() LIMIT 10")
                results = cursor.fetchall()
            times.append(time.time() - start)
        return times
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(executor.map(worker, [None] * num_threads))
    
    all_times = [time for thread_times in results for time in thread_times]
    return all_times

# 测试异步单次连接的性能
async def test_with_single_connection_async(num_queries, num_concurrency):
    """测试使用异步单次连接的查询性能"""
    async def worker():
        times = []
        for _ in range(num_queries // num_concurrency):
            start = time.time()
            async with get_single_connection_async() as conn:
                async with conn.execute("SELECT * FROM test_table_async ORDER BY RANDOM() LIMIT 10") as cursor:
                    results = await cursor.fetchall()
            times.append(time.time() - start)
        return times
    
    tasks = [worker() for _ in range(num_concurrency)]
    results = await asyncio.gather(*tasks)
    
    all_times = [time for task_times in results for time in task_times]
    return all_times

# 更新异步测试运行函数
async def run_async_tests():
    """运行所有异步测试，包括单次连接测试"""
    print("\n===== 开始异步测试 =====")
    print("初始化异步测试数据库...")
    await init_test_db_async()
    
    num_queries = 1000  # 总查询次数
    concurrency_levels = [1, 5, 10, 20]  # 测试不同的并发级别
    
    # 收集数据用于可视化
    no_pool_avgs = []
    single_conn_avgs = []
    pool_avgs = []
    no_pool_improvements = []
    pool_improvements = []
    
    for concurrency in concurrency_levels:
        print(f"\n=== 测试 {concurrency} 个并发任务 ===")
        
        # 测试不使用连接池
        print(f"执行不使用连接池的测试 ({num_queries} 次查询)...")
        no_pool_times = await test_without_pool_async(num_queries, concurrency)
        print_stats(no_pool_times, f"不使用连接池 ({concurrency} 个并发任务)")
        
        # 测试使用单次连接
        print(f"执行使用单次连接的测试 ({num_queries} 次查询)...")
        single_conn_times = await test_with_single_connection_async(num_queries, concurrency)
        print_stats(single_conn_times, f"使用单次连接 ({concurrency} 个并发任务)")
        
        # 测试使用连接池
        print(f"执行使用连接池的测试 ({num_queries} 次查询)...")
        pool_times = await test_with_pool_async(num_queries, concurrency)
        print_stats(pool_times, f"使用连接池 ({concurrency} 个并发任务)")
        
        # 比较性能差异
        no_pool_avg = sum(no_pool_times) / len(no_pool_times)
        single_conn_avg = sum(single_conn_times) / len(single_conn_times)
        pool_avg = sum(pool_times) / len(pool_times)
        
        no_pool_improvement = (no_pool_avg - single_conn_avg) / no_pool_avg * 100
        pool_improvement = (no_pool_avg - pool_avg) / no_pool_avg * 100
        
        print(f"\n单次连接性能改进: {no_pool_improvement:.2f}% ({'提升' if no_pool_improvement > 0 else '下降'})")
        print(f"连接池性能改进: {pool_improvement:.2f}% ({'提升' if pool_improvement > 0 else '下降'})")
        
        # 收集数据
        no_pool_avgs.append(no_pool_avg)
        single_conn_avgs.append(single_conn_avg)
        pool_avgs.append(pool_avg)
        no_pool_improvements.append(no_pool_improvement)
        pool_improvements.append(pool_improvement)
    
    # 返回结果
    return (concurrency_levels, 
            no_pool_avgs, single_conn_avgs, pool_avgs,
            no_pool_improvements, pool_improvements)

# 更新同步测试函数
def run_tests():
    """运行所有测试，包括同步和异步，以及单次连接测试"""
    print("==== 开始同步测试 ====")
    print("初始化测试数据库...")
    init_test_db()
    
    num_queries = 1000  # 总查询次数
    thread_counts = [1, 5, 10, 20]  # 测试不同的线程数
    
    # 收集数据用于可视化
    sync_no_pool_avgs = []
    sync_single_conn_avgs = []
    sync_pool_avgs = []
    sync_no_pool_improvements = []
    sync_pool_improvements = []
    
    for num_threads in thread_counts:
        print(f"\n=== 测试 {num_threads} 个线程 ===")
        
        # 测试不使用连接池
        print(f"执行不使用连接池的测试 ({num_queries} 次查询)...")
        no_pool_times = test_without_pool(num_queries, num_threads)
        print_stats(no_pool_times, f"不使用连接池 ({num_threads} 个线程)")
        
        # 测试使用单次连接
        print(f"执行使用单次连接的测试 ({num_queries} 次查询)...")
        single_conn_times = test_with_single_connection(num_queries, num_threads)
        print_stats(single_conn_times, f"使用单次连接 ({num_threads} 个线程)")
        
        # 测试使用连接池
        print(f"执行使用连接池的测试 ({num_queries} 次查询)...")
        pool_times = test_with_pool(num_queries, num_threads)
        print_stats(pool_times, f"使用连接池 ({num_threads} 个线程)")
        
        # 比较性能差异
        no_pool_avg = sum(no_pool_times) / len(no_pool_times)
        single_conn_avg = sum(single_conn_times) / len(single_conn_times)
        pool_avg = sum(pool_times) / len(pool_times)
        
        no_pool_improvement = (no_pool_avg - single_conn_avg) / no_pool_avg * 100
        pool_improvement = (no_pool_avg - pool_avg) / no_pool_avg * 100
        
        print(f"\n单次连接性能改进: {no_pool_improvement:.2f}% ({'提升' if no_pool_improvement > 0 else '下降'})")
        print(f"连接池性能改进: {pool_improvement:.2f}% ({'提升' if pool_improvement > 0 else '下降'})")
        
        # 收集数据
        sync_no_pool_avgs.append(no_pool_avg)
        sync_single_conn_avgs.append(single_conn_avg)
        sync_pool_avgs.append(pool_avg)
        sync_no_pool_improvements.append(no_pool_improvement)
        sync_pool_improvements.append(pool_improvement)
    
    # 运行异步测试
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # 解决Windows上的问题
    async_results = asyncio.run(run_async_tests())
    
    # 可视化所有结果
    visualize_all_comparison(
        thread_counts, 
        sync_no_pool_avgs, sync_single_conn_avgs, sync_pool_avgs,
        sync_no_pool_improvements, sync_pool_improvements,
        *async_results
    )

if __name__ == "__main__":
    # 兼容性设置
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    run_tests()
