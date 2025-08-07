/**
 * SmartImageFinder 搜索功能相关类型定义
 * 基于最新的搜索功能 API 文档
 */

import { ApiResponse } from './api';
import { SearchImageItem, PaginationMetadata } from './models';

/**
 * 搜索类型枚举
 */
export enum SearchType {
  TITLE = 'title',              // 仅搜索标题
  DESCRIPTION = 'description',  // 仅搜索描述
  BOTH = 'both',                // 同时搜索标题和描述（默认）
  VECTOR = 'vector'             // 使用向量搜索
}

/**
 * 查询类型枚举（用于统一搜索）
 */
export enum QueryType {
  TEXT = 'text',               // 文本查询
  IMAGE = 'image',             // 图像查询
  VECTOR = 'vector'            // 直接向量查询
}

/**
 * 向量搜索目标枚举
 */
export enum VectorSearchTarget {
  TITLE = 'title',              // 标题向量
  DESCRIPTION = 'description',  // 描述向量
  IMAGE = 'image'               // 图像向量
}

/**
 * 向量类型枚举（用于基于向量的搜索）
 */
export enum VectorType {
  TITLE = 'title',              // 标题向量
  DESCRIPTION = 'description',  // 描述向量
  IMAGE = 'image'               // 图像向量（默认）
}

/**
 * 文本搜索请求参数
 */
export interface TextSearchParams {
  q: string;                                   // 搜索关键词
  search_type?: SearchType;                    // 搜索类型
  vector_targets?: VectorSearchTarget[];       // 向量搜索目标，用于 vector 类型
  filename?: string;                           // 按文件名过滤
  tags?: string[];                             // 按标签过滤
  start_date?: string;                         // 开始日期，格式：YYYY-MM-DD HH:MM:SS
  end_date?: string;                           // 结束日期，格式：YYYY-MM-DD HH:MM:SS
  limit?: number;                              // 结果数量限制，默认20
  offset?: number;                             // 分页偏移，默认0
}

/**
 * 图像搜索请求参数
 */
export interface ImageSearchParams {
  file: File;                                   // 上传用于搜索的图片文件
  search_targets?: VectorSearchTarget[];        // 搜索目标，默认为 image
  filename?: string;                            // 按文件名过滤
  tags?: string[];                              // 按标签过滤
  start_date?: string;                          // 开始日期
  end_date?: string;                            // 结束日期
  limit?: number;                               // 结果数量限制
  offset?: number;                              // 分页偏移
}

/**
 * 相似图片搜索路径参数
 */
export interface SimilarSearchPathParams {
  image_id: number | string;                    // 图片ID
}

/**
 * 相似图片搜索查询参数
 * 此接口已更新以匹配后端API：
 * - 使用 `vector_type` 指定单一的搜索向量类型。
 * - 移除了 `search_targets` 和 `search_type`。
 */
export interface SimilarSearchQueryParams {
  vector_type: VectorType;                       // 搜索时使用的向量类型 (e.g., 'image', 'title', 'description')
  filename?: string;                             // 按文件名过滤
  tags?: string[];                               // 按标签过滤
  start_date?: string;                           // 开始日期
  end_date?: string;                             // 结束日期
  limit?: number;                                // 结果数量限制
  offset?: number;                               // 分页偏移
}

/**
 * 基于向量的搜索参数
 */
export interface VectorSearchParams {
  q: string;                                     // 搜索文本，将转换为向量
  vector_type?: VectorType;                      // 要搜索的向量类型
  filename?: string;                             // 按文件名过滤
  tags?: string[];                               // 按标签过滤
  start_date?: string;                           // 开始日期
  end_date?: string;                             // 结束日期
  limit?: number;                                // 结果数量限制
  offset?: number;                               // 分页偏移
}

/**
 * 过滤搜索参数
 */
export interface FilteredSearchParams {
  filename?: string;                             // 按文件名过滤
  title?: string;                                // 按标题过滤
  description?: string;                          // 按描述过滤
  tags?: string[];                               // 按标签过滤
  start_date?: string;                           // 开始日期
  end_date?: string;                             // 结束日期
  limit?: number;                                // 结果数量限制，默认100
  offset?: number;                               // 分页偏移
}

/**
 * 统一搜索参数（文本查询）
 */
export interface UnifiedTextSearchParams {
  q: string;                                     // 搜索文本
  search_type?: SearchType;                      // 搜索类型，默认为 vector
  vector_targets?: VectorSearchTarget[];         // 向量搜索目标
  filename?: string;                             // 按文件名过滤
  tags?: string[];                               // 按标签过滤
  start_date?: string;                           // 开始日期
  end_date?: string;                             // 结束日期
  limit?: number;                                // 结果数量限制
  offset?: number;                               // 分页偏移
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
export type TextSearchResponse = ApiResponse<SearchImageItem[]> & {
  metadata: SearchMetadata;
};

/**
 * 图像搜索响应
 */
export type ImageSearchResponse = ApiResponse<SearchImageItem[]> & {
  metadata: SearchMetadata;
};

/**
 * 相似图片搜索响应
 */
export type SimilarSearchResponse = ApiResponse<SearchImageItem[]> & {
  metadata: SearchMetadata;
};

/**
 * 基于向量的搜索响应
 */
export type VectorSearchResponse = ApiResponse<SearchImageItem[]> & {
  metadata: SearchMetadata;
};

/**
 * 过滤搜索响应
 */
export type FilteredSearchResponse = ApiResponse<SearchImageItem[]> & {
  metadata: SearchMetadata;
};

/**
 * 统一搜索响应
 */
export type UnifiedSearchResponse = ApiResponse<SearchImageItem[]> & {
  metadata: SearchMetadata;
};

/**
 * 搜索错误代码
 */
export enum SearchErrorCode {
  NO_FILTERS = 'NO_FILTERS',                            // 未提供过滤条件
  INVALID_SEARCH_TYPE = 'INVALID_SEARCH_TYPE',          // 不支持的搜索类型
  IMAGE_NOT_FOUND = 'IMAGE_NOT_FOUND',                  // 图片不存在
  DATABASE_ERROR = 'DATABASE_ERROR',                    // 数据库错误
  SEARCH_ERROR = 'SEARCH_ERROR',                        // 一般性搜索错误
  IMAGE_SEARCH_ERROR = 'IMAGE_SEARCH_ERROR',            // 图片处理或向量生成失败
  VECTOR_SEARCH_ERROR = 'VECTOR_SEARCH_ERROR',          // 向量搜索过程中的错误
  SIMILAR_SEARCH_ERROR = 'SIMILAR_SEARCH_ERROR',        // 相似图像搜索过程中的错误
  FILTER_SEARCH_ERROR = 'FILTER_SEARCH_ERROR',          // 过滤搜索过程中的错误
  UNIFIED_SEARCH_ERROR = 'UNIFIED_SEARCH_ERROR',        // 统一搜索过程中的错误
  UNIFIED_IMAGE_SEARCH_ERROR = 'UNIFIED_IMAGE_SEARCH_ERROR', // 统一图像搜索过程中的错误
  UNIFIED_VECTOR_SEARCH_ERROR = 'UNIFIED_VECTOR_SEARCH_ERROR' // 统一向量搜索过程中的错误
}

/**
 * 搜索服务客户端接口
 */
export interface SearchClient {
  /**
   * 文本搜索
   * @param params 文本搜索参数
   * @returns 搜索结果 Promise
   */
  textSearch(params: TextSearchParams): Promise<TextSearchResponse>;
  
  /**
   * 图像搜索
   * @param params 图像搜索参数
   * @returns 搜索结果 Promise
   */
  imageSearch(params: ImageSearchParams): Promise<ImageSearchResponse>;
  
  /**
   * 相似图片搜索
   * @param imageId 图片ID
   * @param params 相似搜索查询参数
   * @returns 搜索结果 Promise
   */
  similarSearch(imageId: number | string, params?: SimilarSearchQueryParams): Promise<SimilarSearchResponse>;
  
  /**
   * 基于向量的搜索
   * @param params 向量搜索参数
   * @returns 搜索结果 Promise
   */
  vectorSearch(params: VectorSearchParams): Promise<VectorSearchResponse>;
  
  /**
   * 过滤搜索
   * @param params 过滤搜索参数
   * @returns 搜索结果 Promise
   */
  filteredSearch(params: FilteredSearchParams): Promise<FilteredSearchResponse>;
  
  /**
   * 统一文本搜索（推荐使用）
   * @param params 统一文本搜索参数
   * @returns 搜索结果 Promise
   */
  unifiedTextSearch(params: UnifiedTextSearchParams): Promise<UnifiedSearchResponse>;
  
  /**
   * 统一图像搜索（推荐使用）
   * @param params 统一图像搜索参数
   * @returns 搜索结果 Promise
   */
  unifiedImageSearch(params: UnifiedImageSearchParams): Promise<UnifiedSearchResponse>;
  
  /**
   * 统一向量搜索（推荐使用）
   * @param params 统一向量搜索参数
   * @returns 搜索结果 Promise
   */
  unifiedVectorSearch(params: UnifiedVectorSearchParams): Promise<UnifiedSearchResponse>;
}
