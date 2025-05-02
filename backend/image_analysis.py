import os
import base64
import hashlib
import json
import time
from typing import Dict, List
from pathlib import Path
import logging
from openai import OpenAI

# 导入项目设置
from .config import settings

# 配置日志记录
logger = logging.getLogger(__name__)

# 多模态提示词模板
MULTIMODAL_PROMPT = """
请分析这张图片并生成一个10字以内的标题、50字以内的图片描述和1-3个以内的关键标签，使用JSON格式输出。

分析以下方面:
1. 图像类型（图表、示意图、照片等）
2. 主要内容/主题
3. 包含的关键信息点
4. 图像的可能用途

输出格式必须严格为:
{
  "title": "简洁标题(10字以内)",
  "description": "详细描述(50字以内)",
  "tags": ["标签1", "标签2", "标签3"]
}

只返回JSON，不要有其他说明文字。
"""


def extract_json_content(text: str) -> Dict[str, str]:
    """
    从文本中提取JSON内容。
    
    参数:
        text (str): 可能包含JSON的文本
    
    返回:
        Dict[str, str]: 解析后的JSON字典，如果解析失败则返回包含错误信息的字典
    """
    if not text:
        return {"error": "Empty response", "title": "", "description": "", "tags": []}
    
    # 尝试寻找JSON的开始和结束位置
    json_start = text.find('{')
    json_end = text.rfind('}')
    
    if (json_start != -1 and json_end != -1 and json_end > json_start):
        try:
            json_text = text[json_start:json_end+1]
            result = json.loads(json_text)
            # 确保返回的字典包含必要的键
            if "title" not in result:
                result["title"] = ""
            if "description" not in result:
                result["description"] = ""
            if "tags" not in result:
                result["tags"] = []
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.debug(f"原始文本: {text}")
            return {"error": f"JSON解析失败: {str(e)}", "title": "", "description": "", "tags": []}
    
    # 如果无法找到有效的JSON，直接尝试解析整个文本
    try:
        result = json.loads(text)
        # 确保返回的字典包含必要的键
        if "title" not in result:
            result["title"] = ""
        if "description" not in result:
            result["description"] = ""
        if "tags" not in result:
            result["tags"] = []
        return result
    except json.JSONDecodeError:
        # 如果整个文本也不是有效的JSON，返回错误信息
        logger.error(f"无法从文本中提取JSON: {text}")
        return {"error": "无法提取JSON内容", "title": "", "description": text[:50], "tags": []}


def image_to_base64(image_path: str) -> str:
    """
    将图像文件转换为Base64编码的字符串。

    参数:
    image_path (str): 图像文件路径。

    返回:
    str: Base64编码的字符串。
    """
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string


def get_image_hash(image_path: str) -> str:
    """
    计算图片文件的部分内容哈希值，用于快速识别
    
    通过读取文件的前8K和后8K内容生成哈希值，对于小于16K的文件直接读取全部内容
    
    参数:
        image_path: 图片文件的路径
        
    返回:
        图片文件的16进制哈希值字符串
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"文件不存在: {image_path}")
    
    hash_obj = hashlib.sha256()
    file_size = os.path.getsize(image_path)
    
    with open(image_path, 'rb') as f:
        # 如果文件小于16K，直接读取全部内容
        if file_size <= 16 * 1024:
            hash_obj.update(f.read())
        else:
            # 读取前8K
            front_chunk = f.read(8 * 1024)
            hash_obj.update(front_chunk)
            
            # 移动到文件末尾前8K的位置
            f.seek(-8 * 1024, os.SEEK_END)
            
            # 读取后8K
            rear_chunk = f.read(8 * 1024)
            hash_obj.update(rear_chunk)
    
    return hash_obj.hexdigest()


class ImageAnalysis:
    """
    图像文本提取器类，用于将图像内容转换为文本描述和标题。
    
    该类使用OpenAI的多模态模型分析图像内容，生成描述性文本和标题。
    """

    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        prompt: str | None = None,
    ):
        """
        初始化 ImageAnalysis 实例。

        参数:
            api_key: API 密钥，如果未提供则从设置中读取
            base_url: API 基础 URL，如果未提供则从设置中读取
            prompt: 自定义提示文本，如果不提供则使用默认提示
        """
        # 优先使用传入的API密钥，否则从设置中读取
        self.api_key = api_key or settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        
        # 确保有可用的API密钥
        if not self.api_key:
            logger.warning("未提供API密钥，多模态功能将无法使用")
            
        # 设置基础URL
        self.base_url = base_url or settings.OPENAI_API_BASE
        
        # 初始化API客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )
        
        # 设置提示词
        self._prompt = prompt or MULTIMODAL_PROMPT
        
        logger.info("多模态图像分析器初始化完成")
    
    def is_model_available(self, model_name: str = None) -> bool:
        """
        检查指定的模型是否可用。
        
        参数:
            model_name: 要检查的模型名称，如果为None，则检查当前默认模型
            
        返回:
            bool: 如果模型可用，则返回True，否则返回False
        """
        if not self.api_key:
            logger.warning("未配置API密钥，无法检查模型可用性")
            return False
            
        try:
            # 确定要检查的模型名称
            model_to_check = model_name or settings.VISION_MODEL
            
            # 获取可用模型列表
            available_models = self.get_available_models()
            
            # 检查指定的模型是否在可用列表中
            return model_to_check in available_models
            
        except Exception as e:
            logger.error(f"检查模型可用性时出错: {str(e)}")
            return False
            
    def get_available_models(self) -> List[str]:
        """
        获取系统中可用的多模态模型列表。
        
        返回:
            List[str]: 可用模型名称列表
        """
        # 如果没有API密钥，则无法获取可用模型
        if not self.api_key:
            logger.warning("未配置API密钥，无法获取可用模型列表")
            return []
            
        try:
            # 直接返回配置文件中定义的可用模型列表
            return settings.AVAILABLE_VISION_MODELS
            
        except Exception as e:
            logger.error(f"获取可用模型列表失败: {str(e)}")
            return []

    def analyze_image(
        self,
        image_url: str = None,
        local_image_path: str = None,
        model: str = None,
        detail: str = "low",
        prompt: str = None,
        temperature: float = 0.1,
    ) -> Dict[str, str]:
        """
        分析图像并生成JSON格式的标题和描述。

        参数:
            image_url: 图像的URL
            local_image_path: 本地图像路径
            model: 使用的模型名称
            detail: 细节级别，可选值为 'low', 'high', 'auto'
            prompt: 提示文本，覆盖默认提示
            temperature: 生成文本的温度参数

        返回:
            Dict[str, str]: 包含标题和描述的字典
        """
        if not self.api_key:
            logger.error("未配置API密钥，无法进行图像分析")
            return {"error": "无法分析图像：未配置API密钥", "title": "", "description": "", "tags": []}

        if not image_url and not local_image_path:
            raise ValueError("必须提供image_url或local_image_path中的一个")

        # 准备图像URL
        if local_image_path:
            image_extension = Path(local_image_path).suffix[1:].lower()
            with open(local_image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                image_url = f"data:image/{image_extension};base64,{base64_image}"

        # 设置模型和提示词
        model = model or settings.VISION_MODEL
        prompt_text = prompt or self._prompt

        # 验证细节级别参数
        if detail not in ["low", "high", "auto"]:
            detail = "low"

        start_time = time.time()
        try:
            # 调用API
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url, "detail": detail},
                            },
                            {"type": "text", "text": prompt_text},
                        ],
                    }
                ],
                stream=False,
                temperature=temperature,
            )
            
            # 获取结果
            result = response.choices[0].message.content
            
            # 解析JSON结果
            analysis_result = extract_json_content(result)
            
            end_time = time.time()
            logger.info(f"图像分析完成，耗时: {end_time - start_time:.2f}秒")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"图像分析出错: {str(e)}")
            end_time = time.time()
            logger.info(f"图像分析失败，耗时: {end_time - start_time:.2f}秒")
            return {"error": f"图像分析失败: {str(e)}", "title": "", "description": ""}

if __name__ == "__main__":
    # 示例用法
    image_analyzer = ImageAnalysis(api_key=settings.OPENAI_API_KEY)
    result = image_analyzer.analyze_image(local_image_path="example.jpg")