import apiClient from './apiClient';
import { ImageDetail, TagInfo } from '@/types/models';
import {
  TagClient,
  GetPopularTagsParams, PopularTagsResponse,
  SearchTagsParams, TagSearchResponse,
  GetImagesByTagParams, ImagesByTagResponse,
  GetImagesByMultipleTagsParams, ImagesByMultipleTagsResponse,
  TagMatchMode
} from '@/types/tag';
import type { ApiResponse } from '@/types';
import { validatePagination } from '@/utils/responseValidators';

const tagService: TagClient = {
  /**
   * 获取热门标签
   * GET /api/v1/tags/
   */
  async getPopularTags(params?: GetPopularTagsParams): Promise<PopularTagsResponse> {
    return apiClient.getWithTransform<TagInfo[]>('/tags', { params })
      .then(resp => {
        // 后端已返回 metadata.total，这里仅做存在性断言；若缺失则派生
        if (resp && (!resp.metadata || (resp.metadata && (resp.metadata as any).total == null))) {
          const derived = Array.isArray(resp.data) ? resp.data.length : 0;
          resp.metadata = { ...(resp.metadata || {}), total: derived } as any;
        }
        return resp as PopularTagsResponse;
      });
  },

  /**
   * 搜索标签
   * GET /api/v1/tags/search
   */
  async searchTags(params: SearchTagsParams): Promise<TagSearchResponse> {
    return apiClient.getWithTransform<string[]>('/tags/search', { params })
      .then(resp => {
        if (resp && (!resp.metadata || (resp.metadata as any).total == null)) {
          const derived = Array.isArray(resp.data) ? resp.data.length : 0;
          resp.metadata = { ...(resp.metadata || {}), total: derived } as any;
        }
        return resp as TagSearchResponse;
      });
  },

  /**
   * 根据标签获取图片
   * GET /api/v1/tags/by-tag/{tag}
   */
  async getImagesByTag(params: GetImagesByTagParams): Promise<ImagesByTagResponse> {
    const { tag, ...restParams } = params;
    // API期望分页参数在查询中，而不是路径中
  return apiClient.getWithTransform<ImageDetail[]>(`/tags/by-tag/${tag}`, { params: restParams })
      .then(resp => { validatePagination(resp, 'getImagesByTag'); return resp as ImagesByTagResponse; });
  },

  /**
   * 根据多个标签获取图片
   * GET /api/v1/tags/by-multiple-tags
   */
  async getImagesByMultipleTags(params: GetImagesByMultipleTagsParams): Promise<ImagesByMultipleTagsResponse> {
    const { tags, mode = TagMatchMode.OR, ...restParams } = params;
    const tagsParam = Array.isArray(tags) ? tags.join(',') : tags;
    
  return apiClient.getWithTransform<ImageDetail[]>('/tags/by-multiple-tags', { params: { ...restParams, tags: tagsParam, mode } })
      .then(resp => { validatePagination(resp, 'getImagesByMultipleTags'); return resp as ImagesByMultipleTagsResponse; });
  },
  /**
   * 覆盖更新图片标签
   * 后端当前仅提供 POST /api/v1/tags/{image_id}/update 用于整体替换标签集合。
   * 之前前端假设存在增量 add/remove 接口（/image/{id}/add, DELETE /image/{id}/{tag}）实际并未实现，已移除，避免404。
   */
  async updateImageTags(imageId: number, tags: string[]): Promise<ApiResponse<{ tags: string[] }>> {
    return apiClient.postWithTransform<{ tags: string[] }>(`/tags/${imageId}/update`, tags);
  }
};

export default tagService;
