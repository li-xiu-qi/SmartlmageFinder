/**
 * SmartImageFinder API 类型定义
 * 基于 API 文档定义的标准响应格式
 */

// API 通用响应类型
export interface ApiResponse<T = unknown> {
  status: 'success' | 'error';
  code: number; // HTTP 状态码
  message: string; // 响应消息
  data: T | null;
  error: ApiError | null; // 错误信息，成功时为null
  metadata: ApiMetadata; // 附加元数据
  timestamp: string; // 响应时间戳
  request_id: string; // 请求ID，用于跟踪
}

// API 错误类型
export interface ApiError {
  code: string; // 错误代码，如 "RESOURCE_NOT_FOUND"
  message: string; // 错误详细描述
  details?: Record<string, unknown>; // 错误的具体详情
}

// API 元数据类型
export interface ApiMetadata {
  pagination?: PaginationMetadata; // 分页信息
  [key: string]: unknown; // 其他元数据
}

// 分页元数据
export interface PaginationMetadata {
  page: number; // 当前页码
  page_size: number; // 每页条目数
  total_items: number; // 总条目数
  total_pages: number; // 总页数
}
