/**
 * SmartImageFinder AI推荐功能相关类型定义
 * 基于 AI推荐路由 API 文档定义
 */

import { ApiResponse } from './api';
import { ImageSearchResult } from './models';

/**
 * 查询改写信息
 */
export interface QueryRewriteInfo {
  original_query: string;        // 原始查询
  optimized_query: string;       // AI优化后的查询
  rewrite_success: boolean;      // 改写是否成功
  error?: string;                // 错误信息（如果有）
}

/**
 * AI推荐请求参数
 */
export interface AIRecommendationParams {
  user_query: string;                    // 用户查询，描述想要找的图片内容
  vector_targets?: string[];             // 向量搜索目标，默认为 ["title", "description", "image"]
  tags?: string[];                       // 按标签过滤
  filename?: string;                     // 按文件名过滤
  start_date?: string;                   // 开始日期过滤
  end_date?: string;                     // 结束日期过滤
  limit?: number;                        // 结果数量限制，默认20
  offset?: number;                       // 分页偏移，默认0
}

/**
 * AI推荐响应数据
 */
export interface AIRecommendationData {
  images: ImageSearchResult[];             // 推荐的图片列表
  query_rewrite?: QueryRewriteInfo;      // 查询改写信息
  total_found?: number;                  // 找到的总数
  search_time_ms?: number;               // 搜索耗时
}

/**
 * AI推荐响应
 */
export type AIRecommendationResponse = ApiResponse<AIRecommendationData>;

/**
 * AI推荐错误代码
 */
export enum AIRecommendationErrorCode {
  AI_RECOMMENDATION_ERROR = 'AI_RECOMMENDATION_ERROR',   // AI推荐服务错误
  INVALID_QUERY = 'INVALID_QUERY',                       // 查询内容无效
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE'            // 服务不可用
}

/**
 * AI推荐服务客户端接口
 */
export interface AIRecommendationClient {
  /**
   * AI智能图片推荐
   * @param params 推荐参数
   * @returns 推荐结果的Promise
   */
  getRecommendations(params: AIRecommendationParams): Promise<AIRecommendationResponse>;
}
