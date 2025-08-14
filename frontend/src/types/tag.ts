// filepath: c:\Users\ke\Documents\projects\python_projects\SmartImager\frontend\src\types\tag.ts
/**
 * SmartImager 标签管理功能相关类型定义
 * 基于标签管理 API 文档
 */

import { ApiResponse } from './api';
import { ImageDetail, TagInfo, PaginationMetadata } from './models';

/**
 * 标签匹配模式
 */
export enum TagMatchMode {
  OR = 'or',          // 匹配任一标签（默认）
  AND = 'and'         // 匹配所有标签
}

/**
 * 热门标签请求参数
 */
export interface GetPopularTagsParams {
  limit?: number;      // 返回标签数量，默认50，范围1-200
}

/**
 * 标签搜索请求参数
 */
export interface SearchTagsParams {
  query: string;       // 标签搜索关键字
  limit?: number;      // 返回标签数量，默认20，范围1-100
}

/**
 * 根据标签获取图片的请求参数
 */
export interface GetImagesByTagParams {
  tag: string;         // 标签名称
  page?: number;       // 页码，默认1
  page_size?: number;  // 每页数量，默认20，范围1-100
}

/**
 * 根据多个标签获取图片的请求参数
 */
export interface GetImagesByMultipleTagsParams {
  tags: string[];                 // 多个标签
  mode?: TagMatchMode;            // 匹配模式，默认为 OR
  page?: number;                  // 页码，默认1
  page_size?: number;             // 每页数量，默认20，范围1-100
}

/**
 * 热门标签元数据
 */
export interface PopularTagsMetadata {
  total: number;                 // 系统中的标签总数
}

/**
 * 标签搜索元数据
 */
export interface TagSearchMetadata {
  total: number;                 // 搜索结果总数
}

/**
 * 图片列表元数据（单标签）
 */
export interface ImagesByTagMetadata {
  pagination: PaginationMetadata; // 分页信息
  tag: string;                    // 查询的标签
}

/**
 * 图片列表元数据（多标签）
 */
export interface ImagesByMultipleTagsMetadata {
  pagination: PaginationMetadata; // 分页信息
  tags: string[];                 // 查询的标签列表
  mode: TagMatchMode;             // 使用的匹配模式
}

/**
 * 标签错误代码
 */
export enum TagErrorCode {
  INVALID_TAGS = 'INVALID_TAGS',   // 提供的标签列表无效或为空
  NOT_FOUND = 'NOT_FOUND'          // 指定的图片不存在
}

/**
 * 热门标签响应
 */
export type PopularTagsResponse = ApiResponse<TagInfo[]> & {
  metadata: PopularTagsMetadata;
};

/**
 * 标签搜索响应
 */
export type TagSearchResponse = ApiResponse<string[]> & {
  metadata: TagSearchMetadata;
};

/**
 * 根据标签获取图片响应
 */
export type ImagesByTagResponse = ApiResponse<ImageDetail[]> & {
  metadata: ImagesByTagMetadata;
};

/**
 * 根据多个标签获取图片响应
 */
export type ImagesByMultipleTagsResponse = ApiResponse<ImageDetail[]> & {
  metadata: ImagesByMultipleTagsMetadata;
};

/**
 * 标签管理服务客户端接口
 */
export interface TagClient {
  /**
   * 获取热门标签
   * @param params 可选的限制参数
   * @returns 热门标签列表的Promise
   */
  getPopularTags(params?: GetPopularTagsParams): Promise<PopularTagsResponse>;
  
  /**
   * 搜索标签
   * @param params 搜索参数
   * @returns 匹配的标签列表的Promise
   */
  searchTags(params: SearchTagsParams): Promise<TagSearchResponse>;
  
  /**
   * 根据标签获取图片
   * @param params 标签和分页参数
   * @returns 图片列表的Promise
   */
  getImagesByTag(params: GetImagesByTagParams): Promise<ImagesByTagResponse>;
  
  /**
   * 根据多个标签获取图片
   * @param params 多标签和分页参数
   * @returns 图片列表的Promise
   */
  getImagesByMultipleTags(params: GetImagesByMultipleTagsParams): Promise<ImagesByMultipleTagsResponse>;
  /**
   * 更新图片标签（覆盖方式）
   * @param imageId 图片ID
   * @param tags 新的标签列表（将完全替换旧的标签）
   * @returns 更新后的标签列表Promise
   */
  updateImageTags(imageId: number, tags: string[]): Promise<ApiResponse<{ tags: string[] }>>;
}