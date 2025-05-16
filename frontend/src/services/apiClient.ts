import axios, { AxiosInstance, AxiosResponse, AxiosRequestConfig } from 'axios';
import { ApiResponse } from '@/types/api';

// 配置参数
const API_BASE_URL = '/api'; // 不包含版本，符合后端文档
const API_TIMEOUT = 30000;

// 创建axios实例并扩展类型
interface EnhancedAxiosInstance extends AxiosInstance {
  getWithTransform<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>>;
  postWithTransform<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>>;
  putWithTransform<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>>;
  patchWithTransform<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>>;
  deleteWithTransform<T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>>;
}

// 创建axios实例
const apiClient: EnhancedAxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
}) as EnhancedAxiosInstance;

// 辅助函数，用于处理响应转换
const transformResponse = <T>(response: AxiosResponse): ApiResponse<T> => {
  return response.data as ApiResponse<T>;
};

// 扩展apiClient，添加自动转换响应的方法
apiClient.getWithTransform = async <T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  const response = await apiClient.get(url, config);
  return transformResponse<T>(response);
};

apiClient.postWithTransform = async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  const response = await apiClient.post(url, data, config);
  return transformResponse<T>(response);
};

apiClient.putWithTransform = async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  const response = await apiClient.put(url, data, config);
  return transformResponse<T>(response);
};

apiClient.patchWithTransform = async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  const response = await apiClient.patch(url, data, config);
  return transformResponse<T>(response);
};

apiClient.deleteWithTransform = async <T>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  const response = await apiClient.delete(url, config);
  return transformResponse<T>(response);
};

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加通用请求逻辑，例如添加token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器处理错误
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 统一处理错误
    const errorResponse: ApiResponse<unknown> = {
      status: 'error',
      code: error.response?.status || 500,
      message: error.response?.data?.message || error.message || '未知错误',
      data: null,
      error: {
        code: error.response?.data?.error?.code || 'UNKNOWN_ERROR',
        message: error.response?.data?.error?.message || error.message || '未知错误',
        details: error.response?.data?.error?.details,
      },
      metadata: {},
      timestamp: new Date().toISOString(),
      request_id: 'error-' + Date.now(),
    };
    return Promise.reject(errorResponse);
  }
);

// 导出配置
export { API_BASE_URL, API_TIMEOUT };

// 导出API客户端
export default apiClient;
