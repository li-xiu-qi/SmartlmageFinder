/**
 * SmartImageFinder 搜索功能相关类型定义
 * 基于搜索功能 API 文档
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
  VECTOR = 'vector',            // 使用向量搜索
  HYBRID = 'hybrid'             // 混合搜索（结合向量和文本）
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
 * 文本搜索请求参数
 */
export interface TextSearchParams {
  q: string;                                   // 搜索关键词
  search_type?: SearchType;                    // 搜索类型
  vector_targets?: VectorSearchTarget[];       // 向量搜索目标，用于 vector 或 hybrid 类型
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
  search_targets?: VectorSearchTarget[];        // 搜索目标
  search_type?: SearchType.VECTOR | SearchType.HYBRID; // 搜索类型，仅支持向量和混合
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
 */
export interface SimilarSearchQueryParams {
  search_targets?: VectorSearchTarget[];         // 搜索目标
  search_type?: SearchType.VECTOR | SearchType.HYBRID; // 搜索类型，仅支持向量和混合
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
  total_results: number;         // 搜索结果总数
  execution_time_ms: number;     // 执行时间（毫秒）
  pagination?: PaginationMetadata; // 分页信息
  reference_image?: {            // 相似搜索的参考图片（仅在相似搜索中返回）
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
 * 搜索错误代码
 */
export enum SearchErrorCode {
  UNSUPPORTED_SEARCH_TYPE = 'UNSUPPORTED_SEARCH_TYPE',  // 不支持的搜索类型
  IMAGE_NOT_FOUND = 'IMAGE_NOT_FOUND',                  // 图片不存在
  DATABASE_ERROR = 'DATABASE_ERROR',                    // 数据库错误
  IMAGE_SEARCH_FAILED = 'IMAGE_SEARCH_FAILED'           // 图像搜索失败
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
}