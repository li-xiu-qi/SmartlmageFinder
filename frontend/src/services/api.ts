import axios, { AxiosRequestConfig } from 'axios';
import { 
  ApiResponse, 
  Image, 
  ImageDetail,
  ImageListParams, 
  SearchParams,
  UploadResponse,
  Tag,
  MetadataField,
  SystemStatus,
  TaskStatus
} from '@/types';

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加通用请求逻辑，例如添加token等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // 统一处理错误
    const errorResponse: ApiResponse = {
      status: 'error',
      data: null,
      error: {
        code: error.code || 'UNKNOWN_ERROR',
        message: error.response?.data?.error?.message || error.message || '未知错误',
      },
      metadata: {},
    };
    return Promise.reject(errorResponse);
  }
);

// 定义API服务
export const imageService = {
  // 获取图片列表
  getImages: (params?: ImageListParams): Promise<ApiResponse<{ images: Image[] }>> => {
    return api.get('/images', { params });
  },

  // 获取单张图片详情
  getImageDetail: (uuid: string): Promise<ApiResponse<ImageDetail>> => {
    return api.get(`/images/${uuid}`);
  },

  // 上传图片
  uploadImages: (files: File[], metadata?: Record<string, any>, generateMetadata = false): Promise<ApiResponse<UploadResponse>> => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    formData.append('generate_metadata', String(generateMetadata));
    
    return api.post('/images/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // 更新图片信息
  updateImage: (uuid: string, data: Partial<Image>): Promise<ApiResponse<Partial<Image>>> => {
    return api.patch(`/images/${uuid}`, data);
  },

  // 删除图片
  deleteImage: (uuid: string): Promise<ApiResponse<{ message: string }>> => {
    return api.delete(`/images/${uuid}`);
  },

  // 批量删除图片
  batchDeleteImages: (uuids: string[]): Promise<ApiResponse<{ deleted: number, failed: number }>> => {
    return api.delete('/images', { data: { uuids } });
  },
};

export const searchService = {
  // 文本搜索图片
  searchByText: (params: SearchParams): Promise<ApiResponse<{ results: ImageDetail[] }>> => {
    return api.get('/search/text', { params });
  },

  // 图片搜索图片
  searchByImage: (image: File, params?: Omit<SearchParams, 'q'>): Promise<ApiResponse<{ results: ImageDetail[] }>> => {
    const formData = new FormData();
    formData.append('image', image);
    
    const config: AxiosRequestConfig = { headers: { 'Content-Type': 'multipart/form-data' } };
    if (params) {
      config.params = params;
    }
    
    return api.post('/search/image', formData, config);
  },

  // 相似图片搜索
  searchSimilar: (uuid: string, params?: Omit<SearchParams, 'q'>): Promise<ApiResponse<{ results: ImageDetail[] }>> => {
    return api.get(`/search/similar/${uuid}`, { params });
  },
};

export const tagService = {
  // 获取所有标签
  getTags: (): Promise<ApiResponse<{ tags: Tag[] }>> => {
    return api.get('/tags');
  },

  // 添加图片标签
  addTags: (uuid: string, tags: string[]): Promise<ApiResponse<{ uuid: string, tags: string[] }>> => {
    return api.post(`/images/${uuid}/tags`, { tags });
  },

  // 删除图片标签
  deleteTag: (uuid: string, tag: string): Promise<ApiResponse<{ uuid: string, tags: string[] }>> => {
    return api.delete(`/images/${uuid}/tags/${tag}`);
  },
};

export const metadataService = {
  // 获取元数据字段
  getMetadataFields: (): Promise<ApiResponse<{ fields: MetadataField[] }>> => {
    return api.get('/metadata/fields');
  },

  // 更新图片元数据
  updateMetadata: (uuid: string, metadata: Record<string, string>): Promise<ApiResponse<{ uuid: string, updated_at: string }>> => {
    return api.patch(`/images/${uuid}/metadata`, { metadata });
  },
};

export const aiService = {
  // 为图片生成描述
  generateContent: (
    uuid: string, 
    options: { 
      generate_title?: boolean; 
      generate_description?: boolean; 
      generate_tags?: boolean; 
      detail?: 'low' | 'high'; 
    } = {}
  ): Promise<ApiResponse<{ uuid: string, generated: { title: string, description: string, tags: string[] }, applied: boolean }>> => {
    return api.post(`/ai/generate/${uuid}`, options);
  },

  // 批量生成内容
  batchGenerate: (
    uuids: string[], 
    options: { 
      generate_title?: boolean; 
      generate_description?: boolean; 
      generate_tags?: boolean; 
      detail?: 'low' | 'high'; 
    } = {}
  ): Promise<ApiResponse<{ task_id: string, total_images: number, status: string }>> => {
    return api.post('/ai/batch-generate', { uuids, options });
  },

  // 查询任务状态
  getTaskStatus: (taskId: string): Promise<ApiResponse<TaskStatus>> => {
    return api.get(`/ai/tasks/${taskId}`);
  },

  // 分析图片
  analyzeImage: (uuid: string): Promise<ApiResponse<any>> => {
    return api.post(`/ai/analyze/${uuid}`);
  },

  // 分析上传图片
  analyzeUpload: (image: File): Promise<ApiResponse<any>> => {
    const formData = new FormData();
    formData.append('image', image);
    
    return api.post('/ai/analyze-upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export const systemService = {
  // 获取系统状态
  getSystemStatus: (): Promise<ApiResponse<SystemStatus>> => {
    return api.get('/system/status');
  },

  // 清除缓存
  clearCache: (cacheTypes: ('vector' | 'image_analysis' | 'all')[]): Promise<ApiResponse<{ message: string, details: Record<string, any> }>> => {
    return api.post('/system/clear-cache', { cache_types: cacheTypes });
  },
};

export default {
  imageService,
  searchService,
  tagService,
  metadataService,
  aiService,
  systemService,
};