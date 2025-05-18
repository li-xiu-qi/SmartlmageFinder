import apiClient from './apiClient';
import { ImageModel, TagInfo } from '@/types/models';
import {
  TagClient,
  GetPopularTagsParams, PopularTagsResponse,
  SearchTagsParams, TagSearchResponse,
  GetImagesByTagParams, ImagesByTagResponse,
  GetImagesByMultipleTagsParams, ImagesByMultipleTagsResponse,
  TagMatchMode
} from '@/types/tag';

const tagService: TagClient = {
  /**
   * 获取热门标签
   * GET /api/v1/tags/
   */
  async getPopularTags(params?: GetPopularTagsParams): Promise<PopularTagsResponse> {
    return apiClient.getWithTransform<TagInfo[]>('/tags', { params }) as Promise<PopularTagsResponse>;
  },

  /**
   * 搜索标签
   * GET /api/v1/tags/search
   */
  async searchTags(params: SearchTagsParams): Promise<TagSearchResponse> {
    return apiClient.getWithTransform<string[]>('/tags/search', { params }) as Promise<TagSearchResponse>;
  },

  /**
   * 根据标签获取图片
   * GET /api/v1/tags/by-tag/{tag}
   */
  async getImagesByTag(params: GetImagesByTagParams): Promise<ImagesByTagResponse> {
    const { tag, ...restParams } = params;
    // API期望分页参数在查询中，而不是路径中
    return apiClient.getWithTransform<ImageModel[]>(`/tags/by-tag/${tag}`, { 
      params: restParams 
    }) as Promise<ImagesByTagResponse>;
  },

  /**
   * 根据多个标签获取图片
   * GET /api/v1/tags/by-multiple-tags
   */
  async getImagesByMultipleTags(params: GetImagesByMultipleTagsParams): Promise<ImagesByMultipleTagsResponse> {
    const { tags, mode = TagMatchMode.OR, ...restParams } = params;
    const tagsParam = Array.isArray(tags) ? tags.join(',') : tags;
    
    return apiClient.getWithTransform<ImageModel[]>('/tags/by-multiple-tags', {
      params: {
        ...restParams,
        tags: tagsParam,
        mode,
      }
    }) as Promise<ImagesByMultipleTagsResponse>;
  },
  /**
   * 更新图片标签（覆盖方式）
   * POST /api/v1/tags/{image_id}/update
   */
  async updateImageTags(imageId: number, tags: string[]): Promise<ApiResponse<{ tags: string[] }>> {
    return apiClient.postWithTransform<{ tags: string[] }>(`/tags/${imageId}/update`, tags);
  },

  /**
   * 为图片添加标签
   * POST /api/v1/tags/image/{image_id}/add
   */
  async addTagsToImage(imageId: number, tags: string[]): Promise<ApiResponse<{ tags: string[] }>> {
    return apiClient.postWithTransform<{ tags: string[] }>(`/tags/image/${imageId}/add`, { tags });
  },

  /**
   * 从图片移除标签
   * DELETE /api/v1/tags/image/{image_id}/{tag}
   */
  async removeTagFromImage(imageId: number, tag: string): Promise<ApiResponse<{ tags: string[] }>> {
    return apiClient.deleteWithTransform<{ tags: string[] }>(`/tags/image/${imageId}/${tag}`);
  },
};

export default tagService;
