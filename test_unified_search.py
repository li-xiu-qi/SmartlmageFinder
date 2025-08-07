# 简单测试统一搜索功能
from backend.db_func.repositories.search import SearchRepository
from backend.db_func.utils import get_connection

try:
    conn = get_connection()
    search_repo = SearchRepository(conn)
    
    # 测试统一文本搜索
    print('=== 测试统一文本搜索 ===')
    results = search_repo.unified_search(
        query_type='text',
        query_content='测试',
        search_targets=['title', 'description'],
        filters={},
        limit=3
    )
    
    print(f'找到 {len(results)} 个结果')
    for result in results:
        score = result.get('score', 0)
        print(f'ID: {result["id"]}, 标题: {result["title"][:30]}..., 相似度: {score:.4f}')
        
    print('\n=== 测试过滤功能 ===')
    # 测试带过滤条件的搜索
    filtered_results = search_repo.unified_search(
        query_type='text',
        query_content='风景',
        search_targets=['title', 'description'],
        filters={'tags': ['自然']},
        limit=2
    )
    
    print(f'过滤后找到 {len(filtered_results)} 个结果')
    for result in filtered_results:
        score = result.get('score', 0)
        print(f'ID: {result["id"]}, 标题: {result["title"][:30]}..., 相似度: {score:.4f}')
        
    conn.close()
    print('\n✅ 统一搜索功能测试成功！')
    
except Exception as e:
    print(f'❌ 测试失败: {str(e)}')
    import traceback
    traceback.print_exc()
