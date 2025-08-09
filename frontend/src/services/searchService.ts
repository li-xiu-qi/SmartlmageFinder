/**
 * SmartImageFinder 搜索服务
 * 基于最新的搜索功能 API 文档
 */
import apiClient from './apiClient';
import {
  SearchClient,
  TextSearchResponse,
  SimilarSearchQueryParams,
  SimilarSearchResponse,
  UnifiedTextSearchParams,
  UnifiedImageSearchParams,
  UnifiedVectorSearchParams,
  UnifiedSearchResponse,
  FuzzySearchParams
} from '@/types/search';
import { SearchImageItem } from '@/types/models';

/**
 * 搜索服务实现
 */
const searchService: SearchClient = {
  // 模糊搜索 (LIKE)
  fuzzySearch: (params: FuzzySearchParams): Promise<TextSearchResponse> => {
    const { tags, fields, ...rest } = params;
    const apiParams: Record<string, unknown> = { ...rest };
    if (tags && tags.length > 0) apiParams.tags = tags.join(',');
    if (fields && fields.length > 0) apiParams.fields = fields;
    return apiClient.getWithTransform<SearchImageItem[]>('/search/fuzzy', { params: apiParams }) as Promise<TextSearchResponse>;
  },

  /**
   * 相似图片搜索
   * 后端此接口已更新，现在使用单一的 `vector_type` 参数来指定搜索时使用的向量类型。
   * @param imageId 图片ID
   * @param queryParams 相似搜索查询参数。应包含 `vector_type` (例如: 'image', 'title', 'description') 
   *                    以及可选的过滤参数 (如 `limit`, `offset`, `tags` 等)。
   *                    `SimilarSearchQueryParams` 类型定义 (在 ../types/search.ts 中) 
   */
  similarSearch: (imageId: number | string, queryParams?: SimilarSearchQueryParams): Promise<SimilarSearchResponse> => {
    let apiParams: Record<string, unknown> | undefined = undefined;

    if (queryParams) {
      const { tags, ...rest } = queryParams;
      apiParams = { ...rest }; // 首先展开其他属性

      if (tags && tags.length > 0) {
        apiParams.tags = tags.join(',');
      }
      
      // 如果处理后 apiParams 没有键，则将其设为 undefined，这样 axios 就不会发送查询字符串
      if (Object.keys(apiParams).length === 0) {
        apiParams = undefined;
      }
    }

    return apiClient.getWithTransform<SearchImageItem[]>(
      `/search/similar/${imageId}`,
      { params: apiParams }
    ) as Promise<SimilarSearchResponse>;
  },
  

  /**
   * 统一文本搜索（推荐使用）
   * @param params 统一文本搜索参数
   */
  unifiedTextSearch: (params: UnifiedTextSearchParams): Promise<UnifiedSearchResponse> => {
    const { tags, vector_targets, ...restParams } = params;
    const apiParams: Record<string, unknown> = { ...restParams };
    
    // 处理标签参数
    if (tags && tags.length > 0) {
      apiParams.tags = tags.join(',');
    }
    
    // 处理向量搜索目标参数
    if (vector_targets && vector_targets.length > 0) {
      // 为每个目标创建数组参数
      apiParams['vector_targets[]'] = vector_targets;
    }
    
    return apiClient.getWithTransform<SearchImageItem[]>('/search/unified', { 
      params: apiParams 
    }) as Promise<UnifiedSearchResponse>;
  },

  /**
   * 统一图像搜索（推荐使用）
   * @param params 统一图像搜索参数
   */
  unifiedImageSearch: (params: UnifiedImageSearchParams): Promise<UnifiedSearchResponse> => {
    const formData = new FormData();
    formData.append('file', params.file);

    if (params.search_targets && params.search_targets.length > 0) {
      params.search_targets.forEach(target => {
        formData.append('search_targets', target);
      });
    }
    
    if (params.filename) {
      formData.append('filename', params.filename);
    }
    
    if (params.tags && params.tags.length > 0) {
      formData.append('tags', params.tags.join(','));
    }
    
    if (params.start_date) {
      formData.append('start_date', params.start_date);
    }
    
    if (params.end_date) {
      formData.append('end_date', params.end_date);
    }
    
    if (typeof params.limit === 'number') {
      formData.append('limit', params.limit.toString());
    }
    
    if (typeof params.offset === 'number') {
      formData.append('offset', params.offset.toString());
    }

    return apiClient.postWithTransform<SearchImageItem[]>('/search/unified/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }) as Promise<UnifiedSearchResponse>;
  },

  /**
   * 统一向量搜索（推荐使用）
   * @param params 统一向量搜索参数
   */
  unifiedVectorSearch: (params: UnifiedVectorSearchParams): Promise<UnifiedSearchResponse> => {
    const formData = new FormData();
    
    // 将向量数组转换为JSON字符串
    formData.append('query_embedding', JSON.stringify(params.query_embedding));

    if (params.search_targets && params.search_targets.length > 0) {
      params.search_targets.forEach(target => {
        formData.append('search_targets', target);
      });
    }
    
    if (params.filename) {
      formData.append('filename', params.filename);
    }
    
    if (params.tags && params.tags.length > 0) {
      formData.append('tags', params.tags.join(','));
    }
    
    if (params.start_date) {
      formData.append('start_date', params.start_date);
    }
    
    if (params.end_date) {
      formData.append('end_date', params.end_date);
    }
    
    if (typeof params.limit === 'number') {
      formData.append('limit', params.limit.toString());
    }
    
    if (typeof params.offset === 'number') {
      formData.append('offset', params.offset.toString());
    }

    return apiClient.postWithTransform<SearchImageItem[]>('/search/unified/vector', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }) as Promise<UnifiedSearchResponse>;
  }
};

export default searchService;
