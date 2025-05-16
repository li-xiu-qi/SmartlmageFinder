from fastapi import UploadFile

from backend.utils.image_analysis import ImageAnalysis
from backend.config import settings

def analyze_upload_image(image_analyzer_instance:ImageAnalysis,
                         upload_image:UploadFile,
                         detail:str="low",):
    """
    分析用户上传的图片，生成标题、描述和标签
    """
    # 
    # 先写入文件到本地的临时保存目录下
    # 然后调用图像分析器的分析方法
    # 生成标题、描述和标签
    # 返回分析结果
    # 清理临时文件
    config = settings.get_config()
    
    temp_file_path = config.TEMP_DIR / upload_image.filename
    with open(temp_file_path, "wb") as f:
        f.write(upload_image.file.read())
        
    # 调用图像分析器的分析方法
    result = image_analyzer_instance.analyze_image(local_image_path=temp_file_path,detail=detail)
    # 清理临时文件
    temp_file_path.unlink(missing_ok=True) # 忽略不存在的文件
    return result