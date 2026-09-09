import os
import base64
import hashlib
import json
import time
from typing import Dict, List
from pathlib import Path
import logging

# 导入项目设置
from ..config import settings
from ..config.init_service import get_openai_client

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


def extract_json_content(text: str) -> Dict[str, any]:
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
    json_start = text.find("{")
    json_end = text.rfind("}")

    if json_start != -1 and json_end != -1 and json_end > json_start:
        try:
            json_text = text[json_start : json_end + 1]
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
            return {
                "error": f"JSON解析失败: {str(e)}",
                "title": "",
                "description": "",
                "tags": [],
            }


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


class ImageAnalysis:
    """
    图像文本提取器类，用于将图像内容转换为文本描述和标题。

    该类使用OpenAI的多模态模型分析图像内容，生成描述性文本和标题。
    """

    def __init__(
        self,
        prompt: str = "",
    ):
        """
        初始化 ImageAnalysis 实例。

        参数:
            prompt: 自定义提示文本，如果不提供则使用默认提示
        """
        # 使用统一的 OpenAI 客户端
        self.client = get_openai_client()
        if not self.client:
            logger.warning("OpenAI 客户端未配置，多模态功能将无法使用")
        self._prompt = prompt or MULTIMODAL_PROMPT
        logger.info("多模态图像分析器初始化完成")


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
        if not self.client:
            logger.error("未配置OpenAI客户端，无法进行图像分析")
            return {
                "error": "无法分析图像：未配置OpenAI客户端或API密钥",
                "title": "",
                "description": "",
                "tags": [],
            }

        if not image_url and not local_image_path:
            raise ValueError("必须提供image_url或local_image_path中的一个")

        # 准备图像URL
        if local_image_path:
            image_extension = Path(local_image_path).suffix[1:].lower()
            with open(local_image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                image_url = f"data:image/{image_extension};base64,{base64_image}"

        # 获取配置对象
        config = settings.get_config()

        # 设置模型和提示词
        model = model or config.VISION_MODEL
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
    image_analyzer = ImageAnalysis()
    result = image_analyzer.analyze_image(local_image_path="example.jpg")
