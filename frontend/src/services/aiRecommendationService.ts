/**
 * SmartImageFinder AI推荐服务
 * 提供AI智能推荐功能
 */

import apiClient from './apiClient';
import {
  AIRecommendationClient,
  AIRecommendationParams,
  AIRecommendationResponse,
  AIRecommendationData
} from '@/types/recommendation';

/**
 * AI推荐服务实现
 */
const aiRecommendationService: AIRecommendationClient = {
  /**
   * AI智能图片推荐
   * GET /api/v1/ai/recommend
   * @param params 推荐参数
   * @returns 推荐结果的Promise
   */
  getRecommendations: async (params: AIRecommendationParams): Promise<AIRecommendationResponse> => {
    const { vector_targets, tags, ...restParams } = params;
    const apiParams: Record<string, unknown> = { ...restParams };
    
    // 处理向量搜索目标参数
    if (vector_targets && vector_targets.length > 0) {
      // 后端期望 vector_targets[] 格式
      vector_targets.forEach(target => {
        if (!apiParams['vector_targets[]']) {
          apiParams['vector_targets[]'] = [];
        }
        (apiParams['vector_targets[]'] as string[]).push(target);
      });
    }
    
    // 处理标签参数
    if (tags && tags.length > 0) {
      apiParams.tags = tags.join(',');
    }
    
    console.log('AI推荐请求参数:', apiParams);
    
    // 支持取消请求的配置
    const requestConfig = { 
      params: apiParams,
      timeout: 60000,  // AI推荐可能需要更长时间，设置60秒超时
      signal: (apiParams as any).signal // 支持AbortController信号
    };
    
    return apiClient.getWithTransform<AIRecommendationData>('/ai/recommend', requestConfig) as Promise<AIRecommendationResponse>;
  }
};

export default aiRecommendationService;
