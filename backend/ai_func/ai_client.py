"""
AI API客户端模块
实现与OpenAI兼容API的交互功能（基础版本）
"""
import json
import requests
from typing import Dict, Any, Optional, List
from ..config import settings


class AIClient:
    """AI API客户端类（基础版本，使用requests）"""
    
    def __init__(self):
        self.api_key = None
        self.api_base = None  
        self.chat_model = None
        self._load_config()
    
    def _load_config(self):
        """加载AI配置"""
        try:
            config = settings.get_config()
            if config:
                self.api_key = config.OPENAI_API_KEY
                self.api_base = config.OPENAI_API_BASE
                self.chat_model = config.CHAT_MODEL or "Qwen/Qwen3-8B"
        except Exception as e:
            print(f"加载AI配置失败: {e}")
            self.chat_model = "Qwen/Qwen3-8B"
    
    def _ensure_config_loaded(self):
        """确保配置已加载（支持运行时配置更新）"""
        if not self.api_key or not self.api_base:
            self._load_config()
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        调用聊天完成API（同步版本）
        
        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
            
        Returns:
            API响应结果
        """
        self._ensure_config_loaded()
        
        if not self.api_key or not self.api_base:
            return {
                "success": False,
                "error": "API密钥或基础URL未配置"
            }
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.chat_model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }
            
            url = f"{self.api_base.rstrip('/')}/chat/completions"
            
            # 不设置超时，让AI有足够时间生成内容
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "content": content,
                        "usage": result.get("usage", {})
                    }
                else:
                    return {
                        "success": False,
                        "error": "API响应格式异常"
                    }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败: {response.status_code} - {response.text}"
                }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"API调用异常: {str(e)}"
            }
    
    async def analyze_and_recommend(
        self,
        query: str,
        context_images: List[Dict[str, Any]],
        search_type: str = "vector",
        target_count: int = 10
    ) -> Dict[str, Any]:
        """
        分析并推荐图片（异步包装器）
        """
        return self.analyze_and_recommend_sync(query, context_images, search_type, target_count)
    
    def analyze_and_recommend_sync(
        self,
        query: str,
        context_images: List[Dict[str, Any]],
        search_type: str = "vector",
        target_count: int = 10
    ) -> Dict[str, Any]:
        """
        分析并推荐图片（同步版本）
        
        Args:
            query: 用户查询
            context_images: 上下文图片信息
            search_type: 搜索类型
            target_count: 目标推荐数量
            
        Returns:
            推荐结果
        """
        try:
            # 准备分析提示词
            prompt = self._build_recommendation_prompt(query, context_images, search_type, target_count)
            
            messages = [
                {"role": "system", "content": "你是一个专业的图片推荐分析师。请仔细分析用户查询和候选图片，返回JSON格式的推荐结果。"},
                {"role": "user", "content": prompt}
            ]
            
            # 调用AI API
            result = self.chat_completion(messages, temperature=0.3, max_tokens=2000)
            
            if result.get("success"):
                try:
                    # 尝试解析JSON响应
                    content = result["content"].strip()
                    
                    # 提取JSON部分（可能包含在代码块中）
                    if "```json" in content:
                        start = content.find("```json") + 7
                        end = content.find("```", start)
                        if end > start:
                            content = content[start:end].strip()
                    elif "```" in content:
                        start = content.find("```") + 3
                        end = content.find("```", start)
                        if end > start:
                            content = content[start:end].strip()
                    
                    recommendation_result = json.loads(content)
                    
                    # 验证响应格式
                    if isinstance(recommendation_result, dict) and "recommended_ids" in recommendation_result:
                        return {
                            "success": True,
                            "recommended_ids": recommendation_result.get("recommended_ids", []),
                            "analysis": recommendation_result.get("analysis", "AI分析完成。")
                        }
                    else:
                        return {
                            "success": False,
                            "error": "AI响应格式不正确"
                        }
                        
                except json.JSONDecodeError as e:
                    print(f"AI响应JSON解析失败: {e}")
                    print(f"原始响应: {result['content']}")
                    return {
                        "success": False,
                        "error": "AI响应格式解析失败"
                    }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"AI推荐分析失败: {str(e)}"
            }
    
    async def chat_with_context(
        self,
        message: str,
        context_images: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        基于上下文进行对话（异步包装器）
        """
        return self.chat_with_context_sync(message, context_images)
    
    def chat_with_context_sync(
        self,
        message: str,
        context_images: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        基于上下文进行对话（同步版本）
        
        Args:
            message: 用户消息
            context_images: 上下文图片信息
            
        Returns:
            对话结果
        """
        try:
            prompt = self._build_chat_prompt(message, context_images or [])
            
            messages = [
                {"role": "system", "content": "你是一个友好的图片助手，帮助用户了解和分析图片内容。请用简洁、自然的语言回答。"},
                {"role": "user", "content": prompt}
            ]
            
            result = self.chat_completion(messages, temperature=0.8, max_tokens=800)
            
            if result.get("success"):
                return {
                    "success": True,
                    "reply": result["content"]
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"AI对话失败: {str(e)}"
            }
    
    def _build_recommendation_prompt(
        self,
        query: str,
        context_images: List[Dict[str, Any]],
        search_type: str,
        target_count: int
    ) -> str:
        """构建推荐分析的提示词"""
        
        # 构建图片信息
        images_info = []
        for i, img in enumerate(context_images, 1):
            tags_str = ", ".join(img.get("tags", [])) if img.get("tags") else "无标签"
            info = f"""
图片{i}: ID={img.get('id')}
  - 标题: {img.get('title') or '无标题'}
  - 描述: {img.get('description') or '无描述'}
  - 标签: {tags_str}
  - 文件名: {img.get('filename', '')}
  - 相似度: {img.get('score', 0):.3f}
  - 文件类型: {img.get('file_type', '')}"""
            images_info.append(info)
        
        images_context = "\n".join(images_info)
        
        prompt = f"""请基于用户查询分析候选图片，并推荐最相关的图片。

用户查询: "{query}"
搜索类型: {search_type}
需要推荐数量: {target_count}

候选图片信息:
{images_context}

请按以下JSON格式返回推荐结果：

{{
    "recommended_ids": [推荐的图片ID列表，按推荐度从高到低排序],
    "analysis": "详细的推荐分析说明，解释推荐理由"
}}

分析要求：
1. 综合考虑标题、描述、标签与查询的匹配程度
2. 考虑图片的相似度得分
3. 优先推荐内容最相关、质量较好的图片
4. 推荐数量不超过{target_count}个
5. 提供具体的推荐理由

请只返回JSON格式，不要添加其他文字。"""

        return prompt
    
    def _build_chat_prompt(
        self,
        message: str,
        context_images: List[Dict[str, Any]]
    ) -> str:
        """构建对话提示词"""
        
        if not context_images:
            return f"""用户问题: {message}

请作为图片助手回答用户的问题。由于没有具体的图片上下文，请给出通用性的建议或询问用户需要什么样的图片信息。"""
        
        # 构建图片上下文
        images_context = []
        for i, img in enumerate(context_images, 1):
            tags_str = ", ".join(img.get("tags", [])) if img.get("tags") else "无"
            context = f"""图片{i}:
- 标题: {img.get('title') or '无'}
- 描述: {img.get('description') or '无'}  
- 标签: {tags_str}
- 文件名: {img.get('filename', '')}"""
            images_context.append(context)
        
        images_info = "\n\n".join(images_context)
        
        prompt = f"""用户正在查看以下图片，请基于这些图片信息回答用户的问题。

相关图片信息:
{images_info}

用户问题: {message}

请提供有帮助的、具体的回答。如果问题与图片内容相关，请结合图片信息回答。回答要简洁明了、自然友好。"""

        return prompt


# 全局AI客户端实例
ai_client = AIClient()
