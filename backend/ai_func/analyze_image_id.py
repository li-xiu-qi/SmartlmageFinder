from backend.utils.image_analysis import ImageAnalysis
from backend.db_func.core import get_db_connection
from backend.db_func.images_func.get import get_image_by_id
import os


def analyze_image_id(image_analyzer_instance:ImageAnalysis,
                     image_id:str,
                     detail:str="low",
                     conn=None):
    """
    分析图片并生成标题、描述和标签
    
    Args:
        image_analyzer_instance: 图像分析器实例
        image_id: 图片ID
        detail: 分析详细程度，"low"或"high"
        conn: 数据库连接对象，使用依赖注入方式传入
    """
    if not image_analyzer_instance:
        return {
            "error": "图像分析服务不可用，请确认配置了正确的API密钥",
            "title": "",
            "description": "",
            "tags": []
        }
    
    try:
        # 从数据库获取图片信息
            
        image = get_image_by_id(conn, int(image_id))
        

        
        if not image:
            return {
                "error": f"找不到ID为{image_id}的图片",
                "title": "",
                "description": "",
                "tags": []
            }
            
        # 获取图片路径
        image_path = image.get("filepath")
        
        if not image_path or not os.path.exists(image_path):
            return {
                "error": f"图片文件路径不正确或文件不存在: {image_path}",
                "title": "",
                "description": "",
                "tags": []
            }
            
        # 调用图像分析器的分析方法
        result = image_analyzer_instance.analyze_image(
            local_image_path=image_path,
            detail=detail
        )
        
        return result
    except Exception as e:
        return {
            "error": f"分析图片时出错: {str(e)}",
            "title": "",
            "description": "",
            "tags": []
        }
    