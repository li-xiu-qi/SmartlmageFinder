/**
 * API配置文件
 * 集中管理所有与API相关的配置
 */

// API版本
export const API_VERSION = 'v1';

// API基础URL
export const API_BASE_URL = `/api/${API_VERSION}`;

// 请求超时时间(毫秒)
export const API_TIMEOUT = 30000;



// 导出默认配置
export default {
  API_VERSION,
  API_BASE_URL,
  API_TIMEOUT,
};
