// API 通用响应类型
export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  data: T | null;
  error: ApiError | null;
  metadata: Record<string, any>;
}

// API 错误类型
export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

// 图片类型
export interface Image {
  uuid: string;
  title: string;
  description: string;
  filepath: string;
  filename?: string;
  file_size?: number;
  file_type?: string;
  width?: number;
  height?: number;
  created_at: string;
  updated_at?: string;
  tags: string[];
  metadata?: Record<string, string>;
}

// 详细图片类型（包含完整信息）
export interface ImageDetail extends Image {
  file_size: number;
  file_type: string;
  width: number;
  height: number;
  metadata: Record<string, string>;
}

// 图片搜索结果类型
export interface ImageSearchResult extends Image {
  score: number;
}

// 图片列表查询参数
export interface ImageListParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
  start_date?: string;
  end_date?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

// 搜索查询参数
export interface SearchParams {
  q?: string;
  mode?: 'vector' | 'text' | 'hybrid';
  field?: 'title' | 'description' | 'all';
  limit?: number;
  filter?: Record<string, any>;
  start_date?: string;
  end_date?: string;
  tags?: string[];
}

// 图片上传响应
export interface UploadResponse {
  uploaded: UploadedImage[];
  failed: FailedUpload[];
}

interface UploadedImage {
  uuid: string;
  original_filename: string;
  file_size: number;
  stored_path: string;
}

interface FailedUpload {
  filename: string;
  error: string;
}

// 标签类型
export interface Tag {
  name: string;
  count: number;
}

// 元数据字段类型
export interface MetadataField {
  name: string;
  count: number;
  type: string;
}

// 系统状态类型
export interface SystemStatus {
  system: {
    version: string;
    uptime: number;
    status: string;
  };
  components: {
    model: {
      status: string;
      name: string;
      load_time: string;
    };
    database: {
      status: string;
      type: string;
      version: string;
    };
    multimodal_api: {
      status: string;
      model: string;
    };
  };
  storage: {
    total_images: number;
    total_size_mb: number;
  };
}

// AI生成内容响应
export interface GeneratedContent {
  title?: string;
  description?: string;
  tags?: string[];
}

// AI生成任务状态
export interface TaskStatus {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: {
    total: number;
    processed: number;
    succeeded: number;
    failed: number;
  };
  results?: TaskResult[];
}

interface TaskResult {
  uuid: string;
  status: 'success' | 'error';
  error?: string;
}