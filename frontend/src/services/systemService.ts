import apiClient from './apiClient';
import { ApiResponse } from '../types/api'; // Changed from @/types
import {
  SystemStatusData,
  SystemConfig,
  CacheStatsData,
  CacheClearData
} from '../types/system';

const systemService = {
  /**
   * 获取系统状态
   * GET /api/system/status
   */
  getSystemStatus: (): Promise<ApiResponse<SystemStatusData>> => {
    return apiClient.getWithTransform<SystemStatusData>('/system/status');
  },

  /**
   * 获取系统配置
   * GET /api/system/config
   */
  getSystemConfig: (): Promise<ApiResponse<SystemConfig>> => {
    return apiClient.getWithTransform<SystemConfig>('/system/config');
  },

  /**
   * 更新系统配置
   * POST /api/system/update-config
   */
  updateSystemConfig: (config: SystemConfig): Promise<ApiResponse<{ message: string }>> => {
    return apiClient.postWithTransform<{ message: string }>('/system/update-config', config);
  },

  /**
   * 获取缓存统计信息
   * GET /api/system/cache-stats
   */
  getCacheStats: (): Promise<ApiResponse<CacheStatsData>> => {
    return apiClient.getWithTransform<CacheStatsData>('/system/cache-stats');
  },

  /**
   * 清除系统缓存
   * POST /api/system/clear-cache
   */
  clearCache: (): Promise<ApiResponse<CacheClearData>> => {
    return apiClient.postWithTransform<CacheClearData>('/system/clear-cache', {});
  }
};

export default systemService;
