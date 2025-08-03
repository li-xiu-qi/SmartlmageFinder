/**
 * AI推荐功能相关的自定义Hook
 */

import { useState, useCallback, useRef } from 'react';
import { message } from 'antd';
import { aiRecommendationService } from '@/services/api';
import {
  AIRecommendationParams,
  AIRecommendationData
} from '@/types/recommendation';

/**
 * AI推荐Hook的返回值类型
 */
export interface UseAIRecommendationReturn {
  // 状态
  loading: boolean;
  
  // 推荐相关
  recommendResults: AIRecommendationData | null;
  getRecommendations: (query: string, options?: Partial<AIRecommendationParams>) => Promise<void>;
  clearRecommendResults: () => void;
  cancelRequest: () => void;
}

/**
 * AI推荐功能Hook
 * 提供AI推荐功能的状态管理和方法
 */
export const useAIRecommendation = (): UseAIRecommendationReturn => {
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // 推荐相关状态
  const [recommendResults, setRecommendResults] = useState<AIRecommendationData | null>(null);

  /**
   * 获取AI推荐
   */
  const getRecommendations = useCallback(async (
    query: string, 
    options: Partial<AIRecommendationParams> = {}
  ) => {
    if (!query.trim()) {
      message.warning('请输入您想要找的图片内容描述');
      return;
    }

    // 取消之前的请求
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // 创建新的取消控制器
    abortControllerRef.current = new AbortController();
    
    setLoading(true);
    
    try {
      const params: AIRecommendationParams = {
        user_query: query,
        vector_targets: ['title', 'description', 'image'],
        limit: 20,
        ...options,
        // 传递取消信号
        signal: abortControllerRef.current.signal
      } as any;

      // 显示进度提示
      const hideLoading = message.loading('AI正在分析您的需求，请稍候...', 0);

      const response = await aiRecommendationService.getRecommendations(params);
      
      // 隐藏加载提示
      hideLoading();
      
      if (response.status === 'success' && response.data) {
        setRecommendResults(response.data);
        
        // 显示查询改写信息
        if (response.data.query_rewrite) {
          const { original_query, optimized_query, rewrite_success } = response.data.query_rewrite;
          if (rewrite_success && original_query !== optimized_query) {
            message.info(`AI已优化您的搜索：${original_query} → ${optimized_query}`);
          }
        }
        
        message.success(`找到 ${response.data.images?.length || 0} 个推荐结果`);
      } else {
        message.error(response.message || 'AI推荐服务出错');
      }
    } catch (error: any) {
      console.error('AI推荐错误:', error);
      
      // 检查是否是用户取消的请求
      if (error.name === 'AbortError' || error.code === 'ERR_CANCELED') {
        message.info('已取消推荐请求');
      } else {
        message.error(error.message || 'AI推荐服务暂时不可用，请稍后重试');
      }
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  }, []);

  /**
   * 取消当前请求
   */
  const cancelRequest = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setLoading(false);
      message.info('已取消推荐请求');
    }
  }, []);

  /**
   * 清除推荐结果
   */
  const clearRecommendResults = useCallback(() => {
    setRecommendResults(null);
  }, []);

  return {
    loading,
    
    // 推荐相关
    recommendResults,
    getRecommendations,
    clearRecommendResults,
    cancelRequest
  };
};
