import httpx
import json
from typing import List, Dict, Any, Optional
from app.config import settings
from app.models.schemas import SearchResult

class SearchClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.backend_base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def search_images(self, 
                          query: str,
                          search_type: str = "text",
                          vector_type: str = "image",
                          limit: int = 10,
                          tags: Optional[List[str]] = None,
                          image_id: Optional[int] = None,
                          **kwargs) -> List[SearchResult]:
        """调用后端搜索API获取图片"""
        
        params = {
            "q": query,
            "limit": min(limit, settings.max_search_limit),
            **kwargs
        }
        
        if tags:
            params["tags"] = ",".join(tags)
        
        try:
            if search_type == "text":
                url = f"{self.base_url}/api/v1/search/text"
                params.update({
                    "search_type": "vector",
                    "vector_targets": vector_type
                })
            elif search_type == "vector":
                url = f"{self.base_url}/api/v1/search/by-vector"
                params["vector_type"] = vector_type
            elif search_type == "similar" and image_id:
                url = f"{self.base_url}/api/v1/search/similar/{image_id}"
                params["vector_type"] = vector_type
            elif search_type == "filtered":
                url = f"{self.base_url}/api/v1/search/filtered"
            else:
                url = f"{self.base_url}/api/v1/search/text"
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "success":
                results = []
                for item in data.get("data", []):
                    # 处理tags字段，确保是列表
                    tags = item.get("tags", [])
                    if isinstance(tags, str):
                        try:
                            tags = json.loads(tags)
                        except:
                            tags = [tags]
                    
                    # 处理metadata字段
                    metadata = item.get("metadata", {})
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except:
                            metadata = {}
                    
                    # 构建完整的图片URL
                    image_url = f"{settings.static_images_url}/{item['filename']}"
                    
                    result = SearchResult(
                        id=item["id"],
                        filename=item["filename"],
                        filepath=item["filepath"],
                        title=item.get("title"),
                        description=item.get("description"),
                        tags=tags,
                        file_size=item.get("file_size", 0),
                        file_type=item.get("file_type", ""),
                        width=item.get("width", 0),
                        height=item.get("height", 0),
                        created_at=item.get("created_at", ""),
                        updated_at=item.get("updated_at", ""),
                        metadata=metadata,
                        distance=item.get("distance"),
                        score=item.get("score")
                    )
                    results.append(result)
                
                return results
            else:
                print(f"搜索API错误: {data.get('error', '未知错误')}")
                return []
                
        except Exception as e:
            print(f"搜索请求失败: {e}")
            return []
    
    async def close(self):
        await self.client.aclose()

search_client = SearchClient()