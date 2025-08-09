// filepath: c:\Users\k\Documents\project\programming_project\python_project\importance\SmartImageFinder\frontend\src\types\image.ts
/**
 * SmartImageFinder 图片管理功能相关类型定义
 * 基于图片管理 API 文档
 */

import { ApiResponse } from './api';
import { ImageDetail, PaginationMetadata, DeletedImageInfo } from './models';

/**
 * 图片列表请求参数
 */
export interface GetImagesListParams {
  page?: number;                   // 页码，默认为1
  page_size?: number;              // 每页数量，默认为20，范围1-100
  sort_by?: string;                // 排序字段，默认为 "created_at"
  order?: 'asc' | 'desc';          // 排序方向，默认为 "desc"
  start_date?: string;             // 开始日期过滤，ISO格式
  end_date?: string;               // 结束日期过滤，ISO格式
  tags?: string[] | string;        // 标签过滤，可以是数组或逗号分隔的字符串
}

/**
 * 单个图片请求参数
 */
export interface GetImageDetailParams {
  image_id: number | string;       // 图片ID
}

/**
 * 图片上传请求参数
 */
export interface UploadImageParams {
  files: File[] | FileList;        // 图片文件，可以是多个文件
  title?: string;                  // 图片标题
  description?: string;            // 图片描述
  tags?: string[] | string;        // 图片标签，数组或JSON字符串
  metadata?: Record<string, unknown> | string; // 元数据，对象或JSON字符串
}

/**
 * 图片更新请求参数
 */
export interface UpdateImageParams {
  image_id: number | string;       // 图片ID
  title?: string;                  // 图片标题
  description?: string;            // 图片描述
  tags?: string[] | string;        // 图片标签，数组或JSON字符串
  metadata?: Record<string, unknown> | string; // 元数据，对象或JSON字符串
}

/**
 * 图片删除请求参数
 */
export interface DeleteImageParams {
  image_id: number | string;       // 图片ID
}

/**
 * 批量删除图片请求参数
 */
export interface BatchDeleteImageParams {
  image_ids: (number | string)[];  // 图片ID数组
}

/**
 * 批量删除响应结果
 */
export interface BatchDeleteResult {
  success_count: number;           // 成功删除的数量
  failed_count: number;            // 删除失败的数量
  total_count: number;             // 总数量
  failed_ids: (number | string)[]; // 删除失败的ID列表
  errors?: Record<string, string>; // 具体的错误信息，key为image_id，value为错误信息
}

/**
 * 批量删除响应
 */
export type BatchDeleteImageResponse = ApiResponse<BatchDeleteResult>;

/**
 * 图片列表元数据
 */
export interface ImagesListMetadata {
  pagination: PaginationMetadata;  // 分页信息
}

/**
 * 图片管理错误代码
 */
export enum ImageErrorCode {
  IMAGE_LIST_ERROR = 'IMAGE_LIST_ERROR',           // 获取图片列表失败
  IMAGE_NOT_FOUND = 'IMAGE_NOT_FOUND',             // 未找到指定的图片
  UPLOAD_ERROR = 'UPLOAD_ERROR',                   // 上传图片失败
  FILE_TYPE_ERROR = 'FILE_TYPE_ERROR',             // 不支持的文件类型
  FILE_SIZE_ERROR = 'FILE_SIZE_ERROR',             // 文件大小超出限制
  INVALID_UPDATE_DATA = 'INVALID_UPDATE_DATA',     // 无效的更新数据
  DELETE_ERROR = 'DELETE_ERROR'                    // 删除图片失败
}

/**
 * 图片列表响应
 */
export type ImagesListResponse = ApiResponse<ImageDetail[]> & {
  metadata: ImagesListMetadata;
};

/**
 * 单个图片响应
 */
export type ImageDetailResponse = ApiResponse<ImageDetail>;

/**
 * 图片上传响应
 */
export type UploadImagesResponse = ApiResponse<ImageDetail[]>;

/**
 * 图片更新响应
 */
export type UpdateImageResponse = ApiResponse<ImageDetail>;

/**
 * 图片删除响应
 */
export type DeleteImageResponse = ApiResponse<DeletedImageInfo>;

/**
 * 图片管理服务客户端接口
 */
export interface ImageClient {
  /**
   * 获取图片列表
   * @param params 过滤、排序和分页参数
   * @returns 图片列表的Promise
   */
  getImagesList(params?: GetImagesListParams): Promise<ImagesListResponse>;

  /**
   * 获取单个图片详情
   * @param params 包含图片ID的参数
   * @returns 图片详情的Promise
   */
  getImageDetail(params: GetImageDetailParams): Promise<ImageDetailResponse>;

  /**
   * 上传一张或多张图片
   * @param params 上传参数和文件
   * @returns 上传结果的Promise
   */
  uploadImages(params: UploadImageParams): Promise<UploadImagesResponse>;

  /**
   * 更新图片信息
   * @param params 更新参数
   * @returns 更新结果的Promise
   */
  updateImage(params: UpdateImageParams): Promise<UpdateImageResponse>;

  /**
   * 删除图片
   * @param params 删除参数
   * @returns 删除结果的Promise
   */
  deleteImage(params: DeleteImageParams): Promise<DeleteImageResponse>;

  /**
   * 批量删除图片
   * @param params 批量删除参数
   * @returns 批量删除结果的Promise
   */
  batchDeleteImages(params: BatchDeleteImageParams): Promise<BatchDeleteImageResponse>;

  /**
   * 获取图片文件URL
   * @param imageId 图片ID
   * @returns 可访问的图片URL
   */
  getImageUrl(imageId: number | string): string;
}
