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
   * AI智能图片推荐（对话式推荐入口）
   * 后端实际提供的是 POST /api/v1/ai/recommend/chat
   * 我们构造一个最小对话（单条 user 消息）即可获得推荐结果。
   */
  getRecommendations: async (params: AIRecommendationParams & { signal?: AbortSignal }): Promise<AIRecommendationResponse> => {
    const {
      user_query,
      vector_targets,
      tags,
      filename,
      start_date,
      end_date,
      limit = 20,
      offset, // 后端 ChatRecommendRequest 暂无 offset，但可放进 filters 统一传递
      signal,
      ...rest // 预留未来扩展字段
    } = params as any;

    if (!user_query || !user_query.trim()) {
      throw new Error('缺少有效的 user_query');
    }

    // 构造后端需要的请求体（ChatRecommendRequest）
    const body: Record<string, any> = {
      messages: [ { role: 'user', content: user_query } ],
      query: user_query,               // 新后端字段：简化查询传递
      vector_targets: vector_targets && vector_targets.length ? vector_targets : undefined,
      limit,
      filters: {
        // 仅在存在时加入，避免发送 undefined
        ...(tags && tags.length ? { tags } : {}),
        ...(filename ? { filename } : {}),
        ...(start_date ? { start_date } : {}),
        ...(end_date ? { end_date } : {}),
        ...(typeof offset === 'number' ? { offset } : {}),
      },
      // 其余未识别字段仍可透传，以便未来向后兼容
      ...(Object.keys(rest).length ? { extra: rest } : {})
    };

    // Axios 的取消需要放在 config.signal 中
    const requestConfig = {
      timeout: 60000, // AI 推荐可能较慢
      signal
    } as const;

    console.log('AI 推荐请求体 (chat 模式):', body);
    const resp = await apiClient.postWithTransform<AIRecommendationData>('/ai/recommend/chat', body, requestConfig) as AIRecommendationResponse;

    // 后端当前返回 data: { success, images, image_ids, limit }；
    // 这里不做侵入式强制转换，只是保证存在 images 字段供前端消费。
    if (resp?.data && !(resp.data as any).images) {
      (resp.data as any).images = [];
    }
    return resp;
  }
};

export default aiRecommendationService;
