// filepath: c:\Users\k\Documents\project\programming_project\python_project\importance\SmartImageFinder\frontend\src\types\system.ts
/**
 * SmartImageFinder 系统管理功能相关类型定义
 * 基于系统管理 API 文档
 */

import { ApiResponse } from './api';

/**
 * 系统基本信息
 */
export interface SystemInfo {
  version: string;             // 系统版本号
  uptime: number;              // 系统运行时间(秒)
  status: 'healthy' | 'warning' | 'error'; // 系统健康状态
  platform: string;            // 操作系统平台
  python_version: string;      // Python版本
}

/**
 * 数据库状态信息
 */
export interface DatabaseStatus {
  status: 'connected' | 'disconnected' | 'error'; // 数据库连接状态
  type: 'sqlite' | 'postgres' | 'mysql';          // 数据库类型
  path: string;                                   // 数据库文件路径(SQLite)或连接字符串
}

/**
 * 向量数据库驱动状态
 */
export interface VectorDbDriverStatus {
  status: 'available' | 'missing' | 'error';      // 驱动状态
  path: string;                                   // 驱动路径
  error: string | null;                           // 错误信息(如果有)
}

/**
 * 多模态API状态
 */
export interface MultimodalApiStatus {
  status: 'enabled' | 'disabled' | 'error';       // API状态
  model: string;                                  // 当前使用的模型
  available_models: string[];                     // 可用模型列表
  api_base: string;                               // API基础URL
}

/**
 * 组件状态信息
 */
export interface ComponentsStatus {
  database: DatabaseStatus;                        // 数据库状态
  vector_db_driver: VectorDbDriverStatus;          // 向量数据库驱动状态
  multimodal_api: MultimodalApiStatus;             // 多模态API状态
}

/**
 * 存储信息
 */
export interface StorageInfo {
  total_images: number;                            // 总图片数量
  total_size_mb: number;                           // 总大小(MB)
  total_tags: number;                              // 总标签数量
  upload_dir: string;                              // 上传目录路径
}

/**
 * 单个缓存信息
 */
export interface CacheStats {
  path: string;                                    // 缓存路径
  entries: number;                                 // 缓存条目数量
  size_mb: number;                                 // 缓存大小(MB)
}

/**
 * 缓存系统信息
 */
export interface CacheInfo {
  enabled: boolean;                                // 是否启用缓存
  max_size_gb: number;                             // 最大缓存大小(GB)
  text_vector_cache: CacheStats;                   // 文本向量缓存信息
  image_vector_cache: CacheStats;                  // 图像向量缓存信息
}

/**
 * 模型信息
 */
export interface ModelsInfo {
  embedding_model: string;                         // 嵌入模型路径
}

/**
 * 服务器信息
 */
export interface ServerInfo {
  host: string;                                    // 服务器主机
  port: number;                                    // 服务器端口
}

/**
 * 完整系统状态信息
 */
export interface SystemStatusData {
  system: SystemInfo;                              // 系统基本信息
  components: ComponentsStatus;                    // 组件状态
  storage: StorageInfo;                            // 存储信息
  cache: CacheInfo;                                // 缓存信息
  models: ModelsInfo;                              // 模型信息
  server: ServerInfo;                              // 服务器信息
}

/**
 * API配置
 */
export interface ApiConfig {
  apiKey: string;                                  // OpenAI API密钥(部分隐藏)
  baseUrl: string;                                 // OpenAI API基础URL
}

/**
 * 存储配置
 */
export interface StorageConfig {
  rootDirectory: string;                           // 上传根目录
  cacheDirectory: string;                          // 缓存目录
  maxCacheSize: number;                            // 最大缓存大小(GB)
}

/**
 * 模型配置
 */
export interface ModelConfig {
  vectorModel: string;                             // 向量模型名称
  visionModel: string;                             // 视觉模型名称
}

/**
 * 向量数据库配置
 */
export interface VectorDbConfig {
  driverPath: string;                              // 驱动路径
}

/**
 * 系统配置
 */
export interface SystemConfig {
  api: ApiConfig;                                  // API配置
  storage: StorageConfig;                          // 存储配置
  model: ModelConfig;                              // 模型配置
  vectorDb: VectorDbConfig;                        // 向量数据库配置
}

/**
 * 缓存清除结果
 */
export interface CacheClearResult {
  cleared: boolean;                                // 是否成功清除
  entries_removed: number;                         // 移除的条目数
  size_freed_mb: number;                           // 释放的空间大小(MB)
  error: string | null;                            // 错误信息(如果有)
}

/**
 * 缓存清除响应数据
 */
export interface CacheClearData {
  text_vector_cache: CacheClearResult;             // 文本向量缓存清除结果
  image_vector_cache: CacheClearResult;            // 图像向量缓存清除结果
}

/**
 * 缓存统计信息
 */
export interface CacheStatsData {
  text_vector_cache: {
    entries: number;                               // 缓存条目数量
    size_mb: number;                               // 缓存大小(MB)
  };
  image_vector_cache: {
    entries: number;                               // 缓存条目数量
    size_mb: number;                               // 缓存大小(MB)
  };
}

/**
 * 系统管理错误代码
 */
export enum SystemErrorCode {
  CONFIG_UPDATE_ERROR = 'CONFIG_UPDATE_ERROR',     // 配置更新失败
  CACHE_CLEAR_ERROR = 'CACHE_CLEAR_ERROR',         // 缓存清除失败
  SYSTEM_STATUS_ERROR = 'SYSTEM_STATUS_ERROR'      // 获取系统状态失败
}

/**
 * 系统状态响应
 */
export type SystemStatusResponse = ApiResponse<SystemStatusData>;

/**
 * 系统配置响应
 */
export type SystemConfigResponse = ApiResponse<SystemConfig>;

/**
 * 配置更新响应
 */
export type UpdateConfigResponse = ApiResponse<{ message: string }>;

/**
 * 缓存统计响应
 */
export type CacheStatsResponse = ApiResponse<CacheStatsData>;

/**
 * 缓存清除响应
 */
export type ClearCacheResponse = ApiResponse<CacheClearData>;

/**
 * 系统管理服务客户端接口
 */
export interface SystemClient {
  /**
   * 获取系统状态
   * @returns 系统状态信息的 Promise
   */
  getSystemStatus(): Promise<SystemStatusResponse>;
  
  /**
   * 获取系统配置
   * @returns 系统配置信息的 Promise
   */
  getSystemConfig(): Promise<SystemConfigResponse>;
  
  /**
   * 更新系统配置
   * @param config 新的系统配置
   * @returns 更新结果的 Promise
   */
  updateSystemConfig(config: SystemConfig): Promise<UpdateConfigResponse>;
  
  /**
   * 获取缓存统计信息
   * @returns 缓存统计的 Promise
   */
  getCacheStats(): Promise<CacheStatsResponse>;
  
  /**
   * 清除系统缓存
   * @returns 缓存清除结果的 Promise
   */
  clearCache(): Promise<ClearCacheResponse>;
}