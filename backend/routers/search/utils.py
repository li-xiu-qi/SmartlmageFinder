# 搜索路由共用工具函数
from typing import Dict, List, Any, Optional, Union
import json
from ...global_schemas import ResponseModel

def build_filters(
    filename: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    tags: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    构建通用的搜索过滤条件字典
    
    Args:
        filename: 文件名过滤
        title: 标题过滤
        description: 描述过滤
        tags: 标签过滤
        start_date: 开始日期过滤
        end_date: 结束日期过滤
        **kwargs: 其他自定义过滤条件
        
    Returns:
        Dict[str, Any]: 过滤条件字典
    """
    filters = {}
    if filename:
        filters["filename"] = filename
    if title:
        filters["title"] = title
    if description:
        filters["description"] = description
    if tags:
        filters["tags"] = tags
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date
        
    # 添加额外的过滤条件
    for key, value in kwargs.items():
        if value is not None:
            filters[key] = value
            
    return filters

def process_json_fields(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    处理结果列表中的JSON字段
    
    Args:
        results: 查询结果列表
        
    Returns:
        List[Dict[str, Any]]: 处理后的结果列表
    """
    for result in results:
        # 处理标签字段
        if result.get('tags') and isinstance(result['tags'], str):
            try:
                result['tags'] = json.loads(result['tags'])
            except:
                result['tags'] = []
                
        # 处理元数据字段
        if result.get('metadata') and isinstance(result['metadata'], str):
            try:
                result['metadata'] = json.loads(result['metadata'])
            except:
                result['metadata'] = {}
                
    return results

def create_paginated_response(
    results: List[Dict[str, Any]],
    limit: int,
    offset: int,
    total_items: Optional[int] = None,
    message: str = "搜索成功"
) -> Dict[str, Any]:
    """
    创建分页响应
    
    Args:
        results: 查询结果
        limit: 每页条数
        offset: 偏移量
        total_items: 总条数(如果已知)
        message: 成功消息
        
    Returns:
        Dict[str, Any]: 分页响应
    """
    # 如果未提供总数，使用结果长度加偏移量作为估计
    if total_items is None:
        total_items = len(results) + offset
        
    return ResponseModel.paginated_response(
        data=results,
        page=offset // limit + 1,
        page_size=limit,
        total_items=total_items,
        message=message
    )

def handle_search_error(e: Exception, limit: int, offset: int, error_code: str = "SEARCH_ERROR") -> Dict[str, Any]:
    """
    处理搜索错误
    
    Args:
        e: 异常
        limit: 每页条数
        offset: 偏移量
        error_code: 错误代码
        
    Returns:
        Dict[str, Any]: 错误响应
    """
    import traceback
    traceback.print_exc()
    
    return ResponseModel.paginated_error(
        error_code=error_code,
        message=f"搜索失败: {str(e)}",
        http_code=500,
        page=offset // limit + 1,
        page_size=limit
    )
