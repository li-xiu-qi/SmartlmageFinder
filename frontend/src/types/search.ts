/**
 * SmartImageFinder 搜索功能相关类型定义
 * 基于最新的搜索功能 API 文档
 */

import { ApiResponse } from './api';
import { ImageSearchResult, PaginationMetadata } from './models';

/**
 * 搜索类型枚举
 */
export enum SearchType {
  VECTOR = 'vector',            // 统一向量搜索
  FUZZY = 'fuzzy'               // 模糊搜索（独立接口）
}



/**
 * 向量搜索目标枚举
 */
export enum VectorSearchTarget { TITLE = 'title', DESCRIPTION = 'description', IMAGE = 'image' }

/**
 * 向量类型枚举（用于基于向量的搜索）
 */
export enum VectorType { TITLE = 'title', DESCRIPTION = 'description', IMAGE = 'image' }

// 旧的独立文本/图片搜索参数已被统一接口取代，移除 TextSearchParams / ImageSearchParams
// SimilarSearchPathParams 仅路径占位，前端直接传参即可，故移除

/**
 * 相似图片搜索查询参数
 * 此接口已更新以匹配后端API：
 * - 使用 `vector_type` 指定单一的搜索向量类型。
 */
export interface SimilarSearchQueryParams {
  vector_type: VectorType;                       // 使用的单一向量类型
  filename?: string;
  tags?: string[];
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

// VectorSearchParams / FilteredSearchParams 已废弃，改用 unified / fuzzy / similar 接口

/**
 * 统一搜索参数（文本查询）
 */
export interface UnifiedTextSearchParams {
  q: string;                                     // 搜索文本
  vector_targets?: VectorSearchTarget[];         // 向量搜索目标
  filename?: string;                             // 按文件名过滤
  tags?: string[];                               // 按标签过滤
  start_date?: string;                           // 开始日期
  end_date?: string;                             // 结束日期
  limit?: number;                                // 结果数量限制
  offset?: number;                               // 分页偏移
}

export interface FuzzySearchParams {
  q: string;
  fields?: string[];                             // 指定字段: title,description,filename
  tags?: string[];
  start_date?: string;
  end_date?: string;
  limit?: number;
  offset?: number;
}

/**
 * 统一搜索参数（图像查询）
 */
export interface UnifiedImageSearchParams {
  file: File;                                    // 上传用于搜索的图片文件
  search_targets?: VectorSearchTarget[];         // 搜索目标，默认为 image
  filename?: string;                             // 按文件名过滤
  tags?: string[];                               // 按标签过滤
  start_date?: string;                           // 开始日期
  end_date?: string;                             // 结束日期
  limit?: number;                                // 结果数量限制
  offset?: number;                               // 分页偏移
}

/**
 * 统一搜索参数（直接向量查询）
 */
export interface UnifiedVectorSearchParams {
  query_embedding: number[];                     // 查询向量
  search_targets?: VectorSearchTarget[];         // 搜索目标
  filename?: string;                             // 按文件名过滤
  tags?: string[];                               // 按标签过滤
  start_date?: string;                           // 开始日期
  end_date?: string;                             // 结束日期
  limit?: number;                                // 结果数量限制
  offset?: number;                               // 分页偏移
}

/**
 * 搜索元数据
 */
export interface SearchMetadata {
  total_results: number;            // 搜索结果总数
  execution_time_ms: number;        // 执行时间（毫秒）
  pagination?: PaginationMetadata;  // 分页信息
  reference_image?: {               // 相似搜索的参考图片（仅在相似搜索中返回）
    id: number;
    title: string;
  };
}

/**
 * 文本搜索响应
 */
// 统一使用 SearchResponse / SimilarSearchResponse；保留 TextSearchResponse 作为模糊搜索返回类型别名
export type TextSearchResponse = ApiResponse<ImageSearchResult[]> & { metadata: SearchMetadata };
export type SimilarSearchResponse = ApiResponse<ImageSearchResult[]> & { metadata: SearchMetadata };

/**
 * 统一搜索响应
 */
export type UnifiedSearchResponse = ApiResponse<ImageSearchResult[]> & {
  metadata: SearchMetadata;
};

/**
 * 搜索错误代码
 */
export enum SearchErrorCode {
  IMAGE_NOT_FOUND = 'IMAGE_NOT_FOUND',
  UNIFIED_SEARCH_ERROR = 'UNIFIED_SEARCH_ERROR',
  UNIFIED_IMAGE_SEARCH_ERROR = 'UNIFIED_IMAGE_SEARCH_ERROR',
  UNIFIED_VECTOR_SEARCH_ERROR = 'UNIFIED_VECTOR_SEARCH_ERROR',
  SIMILAR_SEARCH_ERROR = 'SIMILAR_SEARCH_ERROR'
}

/**
 * 搜索服务客户端接口
 */
export interface SearchClient {
  similarSearch(imageId: number | string, params?: SimilarSearchQueryParams): Promise<SimilarSearchResponse>;
  unifiedTextSearch(params: UnifiedTextSearchParams): Promise<UnifiedSearchResponse>;
  unifiedImageSearch(params: UnifiedImageSearchParams): Promise<UnifiedSearchResponse>;
  unifiedVectorSearch(params: UnifiedVectorSearchParams): Promise<UnifiedSearchResponse>;
  fuzzySearch(params: FuzzySearchParams): Promise<TextSearchResponse>;
}
