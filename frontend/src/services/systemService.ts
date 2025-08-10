import apiClient from './apiClient';
import type { ApiResponse } from '@/types';
import {
  SystemInfo,
  SystemConfig,
  SimplifiedCacheClearData,
  RuntimeInfo,
  DatabaseInfo,
  StorageInfo,
  CacheInfo,
  VectorDbDriverStatus,
  CacheBriefInfo
} from '@/types/system';

const systemService = {
  /**
   * 获取基本系统信息
   * GET /api/v1/system/info
   */
  getSystemInfo: (): Promise<ApiResponse<SystemInfo>> => {
    return apiClient.getWithTransform<SystemInfo>('/system/info');
  },

  /**
   * 获取数据库状态信息
   * GET /api/v1/system/database
   */
  getDatabaseInfo: (): Promise<ApiResponse<DatabaseInfo>> => {
    return apiClient.getWithTransform<DatabaseInfo>('/system/database');
  },

  /**
   * 获取存储信息
   * GET /api/v1/system/storage
   */
  getStorageInfo: (): Promise<ApiResponse<StorageInfo>> => {
    return apiClient.getWithTransform<StorageInfo>('/system/storage');
  },

  /**
   * 获取缓存信息
   * GET /api/v1/system/cache
   */
  getCacheInfo: (): Promise<ApiResponse<CacheInfo>> => {
    return apiClient.getWithTransform<CacheInfo>('/system/cache');
  },

  /**
   * 获取精简缓存信息（快速刷新）
   * GET /api/v1/system/cache/brief
   */
  getCacheBrief: (): Promise<ApiResponse<CacheBriefInfo>> => {
    return apiClient.getWithTransform<CacheBriefInfo>('/system/cache/brief');
  },

  /**
   * 获取系统配置
   * GET /api/v1/system/config
   */
  getSystemConfig: (): Promise<ApiResponse<SystemConfig>> => {
    return apiClient.getWithTransform<SystemConfig>('/system/config');
  },
  /**
   * 更新系统配置
   * POST /api/v1/system/config/update
   */
  updateSystemConfig: (config: SystemConfig): Promise<ApiResponse<{ message: string }>> => {
    return apiClient.postWithTransform<{ message: string }>('/system/config/update', config);
  },
  /**
   * 清除系统缓存
   * POST /api/v1/system/cache/clear
   * @param textCache 是否清除文本缓存，默认为true
   * @param imageCache 是否清除图像缓存，默认为true
   */
  clearCache: (textCache: boolean = true, imageCache: boolean = true): Promise<ApiResponse<SimplifiedCacheClearData>> => {
    const params = new URLSearchParams();
    params.append('text_cache', textCache.toString());
    params.append('image_cache', imageCache.toString());

    return apiClient.postWithTransform<SimplifiedCacheClearData>('/system/cache/clear', {}, {
      params
    });
  },

  /**
   * 获取系统运行时间信息
   * GET /api/v1/system/runtime
   */
  getRuntime: (): Promise<ApiResponse<RuntimeInfo>> => {
    return apiClient.getWithTransform<RuntimeInfo>('/system/runtime');
  },

  /**
   * 获取向量数据库驱动状态
   * GET /api/v1/system/vector-driver
   */
  getVectorDbDriverStatus: (): Promise<ApiResponse<VectorDbDriverStatus>> => {
    return apiClient.getWithTransform<VectorDbDriverStatus>('/system/vector-driver');
  }
};

export default systemService;
