from typing import Tuple, Optional
from ..utils.image_analysis import ImageAnalysis
from ..config import settings
IMAGE_ANALYZER_INSTANCE = None
AI_AVAILABLE_STATUS = False

def initialize_ai_services() -> Tuple[Optional[ImageAnalysis], bool]:
    """
    初始化AI组件，特别是图像分析服务。

    返回值:
        一个元组，包含ImageAnalysis实例（如果初始化失败则为None）
        和一个布尔值，表示AI功能是否可用。
    """
    global IMAGE_ANALYZER_INSTANCE
    global AI_AVAILABLE_STATUS
    
    try:
        config = settings.get_config()
        api_key = getattr(config, 'OPENAI_API_KEY', "")
        base_url = getattr(config, 'OPENAI_API_BASE', "")

        if not api_key:
            print("AI图像分析服务: API Key 未配置。相关AI功能将不可用。")
            return IMAGE_ANALYZER_INSTANCE, AI_AVAILABLE_STATUS

        current_analyzer = ImageAnalysis(api_key=api_key, base_url=base_url)
        
        IMAGE_ANALYZER_INSTANCE = current_analyzer
        AI_AVAILABLE_STATUS = True
        print("AI图像分析服务已成功初始化。")

    except AttributeError:
        print(f"AI图像分析服务配置错误 (例如，配置项缺失或格式不正确)。相关AI功能将不可用。")
    except Exception as e:
        print(f"初始化AI图像分析器时发生错误: {e}。相关AI功能将不可用。")
        
    return IMAGE_ANALYZER_INSTANCE, AI_AVAILABLE_STATUS


# 定义一个get_image_analyzer函数来获取图像分析器实例，方便依赖注入使用
def get_image_analyzer() -> Optional[ImageAnalysis]:
    """
    获取图像分析器实例。

    返回:
        ImageAnalysis实例，如果未初始化则返回None。
    """
    global IMAGE_ANALYZER_INSTANCE
    return IMAGE_ANALYZER_INSTANCE