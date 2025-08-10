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
  app_uptime: number;          // 系统运行时间(秒)
  app_uptime_formatted: string; // 格式化的运行时间
  status: 'healthy' | 'warning' | 'error'; // 系统健康状态
  platform: string;            // 操作系统平台
  python_version: string;      // Python版本
  models_info?: {              // 模型信息，可选
    embedding_model: string;   // 嵌入模型路径
    embedding_dimension?: number; // 嵌入维度
  };
}

/**
 * 数据库状态信息
 */
export interface DatabaseInfo {
  status: 'connected' | 'disconnected' | 'error'; // 数据库连接状态
  type: 'sqlite' | 'postgres' | 'mysql';          // 数据库类型
  path: string;                                   // 数据库文件路径(SQLite)或连接字符串
  image_count: number;                            // 图片总数
  total_size: number;                             // 总大小(字节)
  tag_count: number;                              // 标签总数
  vector_status: boolean;                         // 向量功能状态
  db_version: string;                             // 数据库版本
  error: string | null;                           // 错误信息(如果有)
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
  database: DatabaseInfo;                        // 数据库状态
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
  path: string;            // 缓存路径
  size_mb: number;         // 缓存目录大小(MB)
  db_file_size_mb?: number;// 底层cache.db文件大小(MB)
}

/**
 * 缓存系统信息
 */
export interface CacheInfo {
  enabled: boolean;        // 是否启用缓存
  max_size_gb: number;     // 最大缓存大小(GB)
  total_size_mb: number;   // 总缓存大小(MB)
  text_vector_cache: CacheStats;
  image_vector_cache: CacheStats;
  last_scan?: number;      // 最近一次统计时间戳(秒)
}

// 精简缓存信息（轮询）
export interface CacheBriefInfo {
  total_size_mb: number;
  last_scan?: number;
  enabled: boolean;
}

export type CacheBriefInfoResponse = ApiResponse<CacheBriefInfo>;

/**
 * 模型信息
 */
export interface ModelsInfo {
  embedding_model: string;                         // 嵌入模型路径
  embedding_dimension?: number;                   // 嵌入维度大小
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
  availableModels: string[];                       // Added to match backend response
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
 * 简化版的缓存清除结果 - 适配新的API响应
 */
export interface SimplifiedCacheClearData {
  cleared: boolean;                                // 是否成功清除
  text_cache_entries_removed: number;              // 移除的文本缓存条目数
  image_cache_entries_removed: number;             // 移除的图像缓存条目数
  total_size_freed_mb: number;                     // 释放的总空间大小(MB)
}

/**
 * 系统管理错误代码
 */
export enum SystemErrorCode {
  CONFIG_UPDATE_ERROR = 'CONFIG_UPDATE_ERROR',     // 配置更新失败
  CACHE_CLEAR_ERROR = 'CACHE_CLEAR_ERROR',         // 缓存清除失败
  SYSTEM_STATUS_ERROR = 'SYSTEM_STATUS_ERROR',     // 获取系统状态失败
  DATABASE_ERROR = 'DATABASE_ERROR',               // 数据库状态错误
  STORAGE_ERROR = 'STORAGE_ERROR',                 // 存储信息错误
  CACHE_ERROR = 'CACHE_ERROR'                      // 缓存信息错误
}

/**
 * 系统状态响应
 */
export type SystemStatusResponse = ApiResponse<SystemStatusData>;

/**
 * 系统基本信息响应
 */
export type SystemInfoResponse = ApiResponse<SystemInfo>;

/**
 * 数据库信息响应
 */
export type DatabaseInfoResponse = ApiResponse<DatabaseInfo>;

/**
 * 存储信息响应
 */
export type StorageInfoResponse = ApiResponse<StorageInfo>;

/**
 * 缓存信息响应
 */
export type CacheInfoResponse = ApiResponse<CacheInfo>;

/**
 * 系统配置响应
 */
export type SystemConfigResponse = ApiResponse<SystemConfig>;

/**
 * 配置更新响应
 */
export type UpdateConfigResponse = ApiResponse<{ message: string }>;

/**
 * 缓存清除响应
 */
export type ClearCacheResponse = ApiResponse<SimplifiedCacheClearData>;

/**
 * 运行时间信息
 */
export interface RuntimeInfo {
  app_uptime_formatted: string;                    // 格式化的运行时间
  current_time: string;                            // 当前服务器时间(ISO格式)
}

/**
 * 运行时间响应
 */
export type RuntimeInfoResponse = ApiResponse<RuntimeInfo>;

/**
 * 系统管理服务客户端接口
 */
export interface SystemClient {
  /**
   * 获取基本系统信息
   * @returns 系统基本信息的 Promise
   */
  getSystemInfo(): Promise<ApiResponse<SystemInfo>>;

  /**
   * 获取数据库状态信息
   * @returns 数据库状态信息的 Promise
   */
  getDatabaseInfo(): Promise<ApiResponse<DatabaseInfo>>;

  /**
   * 获取存储信息
   * @returns 存储信息的 Promise
   */
  getStorageInfo(): Promise<ApiResponse<StorageInfo>>;

  /**
   * 获取缓存信息
   * @returns 缓存信息的 Promise
   */
  getCacheInfo(): Promise<ApiResponse<CacheInfo>>;

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
   * 清除系统缓存
   * @param textCache 是否清除文本缓存
   * @param imageCache 是否清除图像缓存
   * @returns 缓存清除结果的 Promise
   */
  clearCache(textCache?: boolean, imageCache?: boolean): Promise<ClearCacheResponse>;

  /**
   * 获取运行时间信息
   * @returns 运行时间信息的 Promise
   */
  getRuntime(): Promise<RuntimeInfoResponse>;
}
