import openai
import json
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.models.schemas import SearchResult, AIRecommendation

class AIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base
        )
    
    async def generate_recommendations(
        self, 
        query: str, 
        search_results: List[SearchResult],
        search_context: Dict[str, Any]
    ) -> List[AIRecommendation]:
        """基于搜索结果生成AI推荐，处理各种边缘情况"""
        
        if not search_results:
            return []
        
        # 处理无意义标题和描述
        processed_results = self._process_search_results(search_results)
        
        # 构建上下文信息，包含原始相似度和处理后的内容
        context_images = []
        for i, (result, has_meaningful_content) in enumerate(processed_results):
            context_images.append({
                "id": result.id,
                "title": result.title or f"图片_{result.id}",
                "description": result.description or "暂无描述",
                "tags": result.tags or [],
                "filename": result.filename,
                "original_score": result.score,
                "has_meaningful_content": has_meaningful_content,
                "file_info": {
                    "type": result.file_type,
                    "size": f"{result.file_size} bytes",
                    "dimensions": f"{result.width}x{result.height}"
                }
            })
        
        prompt = f"""你是一位专业的图片推荐专家。请基于用户查询和搜索结果，为用户推荐最相关的图片，并处理以下特殊情况：

1. 标题/描述缺失或无意义的情况
2. 相似度高但内容不匹配的情况
3. 需要基于实际内容而非仅相似度进行推荐

用户查询: "{query}"

搜索结果图片信息:
{json.dumps(context_images, ensure_ascii=False, indent=2)}

重要指导原则：
- 不要完全依赖相似度分数，要结合实际内容进行判断
- 对于无意义标题/描述的图片，要根据标签和文件名推断内容
- 识别并纠正相似度与实际内容不符的情况
- 优先推荐真正符合用户需求的图片

请返回JSON格式：
{{
  "recommendations": [
    {{
      "id": 图片ID,
      "relevance_score": 0-1之间的相关性评分,
      "reason": "推荐理由，说明为什么适合用户",
      "confidence": "高/中/低，对推荐的信心程度",
      "content_analysis": "基于实际内容而非相似度的分析",
      "adjustment_note": "如果有调整相似度，说明原因"
    }}
  ],
  "summary": "整体分析总结"
}}

请确保推荐结果真正符合用户的搜索意图。"""

        try:
            response = await self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "你是一个专业的图片推荐专家，擅长分析图片内容与用户需求的相关性，能够识别并纠正相似度与实际内容不符的情况。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2500
            )
            
            ai_response = response.choices[0].message.content
            
            # 解析AI响应
            try:
                ai_data = json.loads(ai_response)
                recommendations = []
                
                for rec in ai_data.get("recommendations", []):
                    image_id = rec.get("id")
                    image_result = next((r for r in search_results if r.id == image_id), None)
                    
                    if image_result:
                        # 使用AI提供的相关性评分，但确保在合理范围
                        relevance_score = max(0.1, min(1.0, rec.get("relevance_score", 0.5)))
                        
                        recommendation = AIRecommendation(
                            image=image_result,
                            ai_reason=rec.get("reason", "基于内容分析推荐"),
                            relevance_score=relevance_score,
                            search_context=search_context
                        )
                        recommendations.append(recommendation)
                
                # 如果没有AI推荐，回退到默认排序
                if not recommendations:
                    return self._fallback_recommendations(search_results, query)
                
                return recommendations
                
            except json.JSONDecodeError:
                # JSON解析失败，使用回退方案
                return self._fallback_recommendations(search_results, query)
                
        except Exception as e:
            print(f"AI服务调用失败: {e}")
            return self._fallback_recommendations(search_results, query)
    
    def _process_search_results(self, search_results: List[SearchResult]) -> List[Tuple[SearchResult, bool]]:
        """处理搜索结果，标记是否有意义的标题/描述"""
        processed = []
        
        for result in search_results:
            title = result.title or ""
            description = result.description or ""
            
            # 检查是否有意义的内容
            has_meaningful_title = bool(title.strip() and len(title.strip()) > 2 and not title.startswith("IMG_"))
            has_meaningful_description = bool(description.strip() and len(description.strip()) > 10)
            
            has_meaningful_content = has_meaningful_title or has_meaningful_description
            
            processed.append((result, has_meaningful_content))
        
        return processed
    
    def _fallback_recommendations(
        self, 
        search_results: List[SearchResult], 
        query: str
    ) -> List[AIRecommendation]:
        """回退方案：基于相似度的智能推荐"""
        recommendations = []
        
        search_context = {
            "query": query,
            "total_results": len(search_results),
            "method": "fallback"
        }
        
        for result in search_results:
            # 基础推荐理由
            reason_parts = []
            
            # 基于相似度
            if result.score and result.score > 0.8:
                reason_parts.append("高度匹配")
            elif result.score and result.score > 0.6:
                reason_parts.append("较好匹配")
            else:
                reason_parts.append("相关匹配")
            
            # 基于内容特征
            if result.title and len(result.title.strip()) > 5:
                reason_parts.append(f"标题包含'{result.title[:20]}...'")
            
            if result.tags and len(result.tags) > 0:
                tag_str = ", ".join(result.tags[:3])
                reason_parts.append(f"标签: {tag_str}")
            
            if result.description and len(result.description.strip()) > 10:
                reason_parts.append("有详细描述")
            
            # 构建推荐理由
            reason = "；".join(reason_parts) if reason_parts else f"基于相似度推荐({result.score:.2f})"
            
            # 调整相关性评分，考虑内容质量
            base_score = result.score or 0.5
            
            # 提升有有意义内容的图片评分
            has_good_content = (
                (result.title and len(result.title.strip()) > 5) or
                (result.description and len(result.description.strip()) > 20) or
                (result.tags and len(result.tags) > 0)
            )
            
            if has_good_content:
                adjusted_score = min(1.0, base_score * 1.1)
            else:
                adjusted_score = base_score
            
            recommendation = AIRecommendation(
                image=result,
                ai_reason=reason,
                relevance_score=adjusted_score,
                search_context=search_context
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_content_insights(self, result: SearchResult) -> Dict[str, str]:
        """生成内容洞察，处理无意义内容"""
        insights = {
            "title_insight": "",
            "description_insight": "",
            "fallback_info": ""
        }
        
        # 处理标题
        title = result.title or ""
        if title.strip() and len(title.strip()) > 2 and not title.startswith("IMG_"):
            insights["title_insight"] = title.strip()
        else:
            insights["title_insight"] = "无意义标题"
            # 从文件名推断
            filename_parts = result.filename.replace(".jpg", "").replace(".png", "").replace("_", " ")
            insights["fallback_info"] = f"文件名: {filename_parts}"
        
        # 处理描述
        description = result.description or ""
        if description.strip() and len(description.strip()) > 10:
            insights["description_insight"] = description.strip()[:100] + "..." if len(description) > 100 else description.strip()
        else:
            insights["description_insight"] = "无详细描述"
        
        return insights
    
    async def generate_search_analysis(
        self, 
        query: str, 
        search_results: List[SearchResult]
    ) -> str:
        """生成智能搜索分析"""
        
        if not search_results:
            return f"抱歉，未找到与'{query}'相关的图片。建议尝试更宽泛的关键词或检查拼写。"
        
        # 分析结果质量
        meaningful_count = 0
        total_tags = set()
        
        for result in search_results:
            title = result.title or ""
            description = result.description or ""
            
            if (title.strip() and len(title.strip()) > 2) or \
               (description.strip() and len(description.strip()) > 10):
                meaningful_count += 1
            
            if result.tags:
                total_tags.update(result.tags)
        
        # 构建分析
        analysis_parts = []
        analysis_parts.append(f"找到了{len(search_results)}张相关图片")
        
        if meaningful_count > 0:
            analysis_parts.append(f"其中{meaningful_count}张有详细的标题或描述")
        
        if total_tags:
            top_tags = list(total_tags)[:5]
            analysis_parts.append(f"主要涉及: {', '.join(top_tags)}")
        
        # 基于相似度分布给出建议
        high_similarity = [r for r in search_results if r.score and r.score > 0.8]
        if high_similarity:
            analysis_parts.append(f"有{len(high_similarity)}张高度匹配的图片")
        
        return "；".join(analysis_parts) + "。AI已为您精选最相关的推荐结果。"

ai_service = AIService()