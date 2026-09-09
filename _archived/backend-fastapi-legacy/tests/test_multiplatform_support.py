"""
数据库驱动多平台支持测试工具
用于验证当前平台的驱动设置是否正常工作
"""
import os
import sys
import sqlite3
from pathlib import Path

# 添加项目根目录到Python路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from backend.config.platform_detector import PlatformDetector, auto_setup_driver
from backend.db_func.core.extensions.loader import setup_connection
from backend.config import settings


def test_platform_detection():
    """测试平台检测功能"""
    print("=" * 50)
    print("平台检测测试")
    print("=" * 50)
    
    platform_info = PlatformDetector.get_platform_info()
    for key, value in platform_info.items():
        print(f"{key}: {value}")
    
    print(f"\n当前平台标识: {PlatformDetector.detect_platform()}")
    print(f"期望的扩展文件名: {PlatformDetector.get_extension_filename()}")


def test_driver_extraction():
    """测试驱动文件提取"""
    print("\n" + "=" * 50)
    print("驱动文件提取测试")
    print("=" * 50)
    
    # 获取驱动目录
    driver_dir = os.path.join(
        project_root, "backend", "config_files", "vector_db_driver"
    )
    
    print(f"驱动目录: {driver_dir}")
    
    # 检查驱动目录是否存在
    if not os.path.exists(driver_dir):
        print(f"错误: 驱动目录不存在: {driver_dir}")
        return False
    
    # 列出驱动目录中的文件
    print("\n驱动目录中的文件:")
    for file in os.listdir(driver_dir):
        file_path = os.path.join(driver_dir, file)
        if os.path.isfile(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  {file} ({file_size} bytes)")
    
    # 尝试自动设置驱动
    print("\n尝试自动设置驱动...")
    success, driver_path = auto_setup_driver(driver_dir, force_extract=True)
    
    if success:
        print(f"✓ 驱动设置成功: {driver_path}")
        if os.path.exists(driver_path):
            file_size = os.path.getsize(driver_path)
            print(f"  文件大小: {file_size} bytes")
        return True
    else:
        print("✗ 驱动设置失败")
        return False


def test_database_connection():
    """测试数据库连接和扩展加载"""
    print("\n" + "=" * 50)
    print("数据库连接测试")
    print("=" * 50)
    
    # 创建临时数据库文件
    test_db_path = os.path.join(project_root, "backend", "tests", "test_multiplatform.db")
    
    # 确保测试目录存在
    os.makedirs(os.path.dirname(test_db_path), exist_ok=True)
    
    # 如果测试数据库已存在，删除它
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    try:
        print(f"创建测试数据库: {test_db_path}")
        
        # 创建数据库连接
        conn = sqlite3.connect(test_db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        print("尝试设置连接和加载扩展...")
        
        # 使用我们的扩展加载器
        success = setup_connection(conn, silent=False)
        
        if success:
            print("✓ 数据库连接和扩展加载成功")
            
            # 测试向量功能
            print("\n测试向量功能...")
            cursor = conn.cursor()
            
            # 创建测试向量表
            cursor.execute("""
                CREATE VIRTUAL TABLE test_vectors USING vec0(
                    id INTEGER PRIMARY KEY,
                    embedding FLOAT[3]
                );
            """)
            
            # 插入测试向量
            cursor.execute("""
                INSERT INTO test_vectors (id, embedding) VALUES (1, '[1.0, 2.0, 3.0]');
            """)
            
            cursor.execute("""
                INSERT INTO test_vectors (id, embedding) VALUES (2, '[4.0, 5.0, 6.0]');
            """)
            
            # 执行向量搜索
            cursor.execute("""
                SELECT id, distance FROM test_vectors 
                WHERE embedding MATCH '[1.1, 2.1, 3.1]' 
                ORDER BY distance 
                LIMIT 1;
            """)
            
            result = cursor.fetchone()
            if result:
                print(f"✓ 向量搜索成功: ID={result[0]}, Distance={result[1]:.4f}")
            else:
                print("✗ 向量搜索失败")
            
            conn.commit()
            
        else:
            print("✗ 数据库连接或扩展加载失败")
            return False
            
    except Exception as e:
        print(f"✗ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()
        
        # 清理测试数据库
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
    return True


def test_config_update():
    """测试配置自动更新"""
    print("\n" + "=" * 50)
    print("配置自动更新测试")
    print("=" * 50)
    
    config = settings.get_config()
    current_driver = config.VECTOR_DB_DRIVER
    
    print(f"当前配置的驱动路径: {current_driver}")
    
    # 检查当前配置的驱动是否适合当前平台
    expected_extension = PlatformDetector.get_extension_filename()
    
    if current_driver and current_driver.endswith(expected_extension):
        print(f"✓ 当前配置的驱动适合当前平台 ({expected_extension})")
    else:
        print(f"⚠ 当前配置的驱动可能不适合当前平台 (期望: {expected_extension})")
        
        # 尝试自动更新配置
        driver_dir = os.path.join(
            project_root, "backend", "config_files", "vector_db_driver"
        )
        
        success, driver_path = auto_setup_driver(driver_dir)
        if success:
            print(f"✓ 可以自动设置适合的驱动: {driver_path}")
        else:
            print("✗ 无法自动设置适合的驱动")


def main():
    """主测试函数"""
    print("数据库驱动多平台支持测试")
    print("时间:", __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 运行所有测试
    tests = [
        ("平台检测", test_platform_detection),
        ("驱动提取", test_driver_extraction),
        ("数据库连接", test_database_connection),
        ("配置更新", test_config_update),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n{test_name}测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # 输出测试结果汇总
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\n总体结果: {'✓ 所有测试通过' if all_passed else '✗ 存在测试失败'}")
    
    return all_passed


if __name__ == "__main__":
    main()
