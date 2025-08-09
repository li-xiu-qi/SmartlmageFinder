/**
 * SmartImageFinder 元数据管理功能相关类型定义
 */

import { ApiResponse } from './api';
import { ImageDetail } from './models';

/**
 * 元数据更新请求参数
 */
export interface UpdateMetadataParams {
  image_id: number | string;       // 图片ID
  metadata: Record<string, string>; // 元数据，键和值都为字符串
}

/**
 * 元数据更新响应
 * 通常会返回更新后的整个图片信息
 */
export type UpdateMetadataResponse = ApiResponse<ImageDetail>;

/**
 * 元数据管理服务客户端接口 (如果需要单独的元数据服务)
 * 如果元数据操作集成在 ImageClient 中，则此接口可能不需要单独创建。
 */
export interface MetadataClient {
  /**
   * 更新图片元数据
   * @param params 更新元数据参数
   * @returns 更新结果的Promise
   */
  updateMetadata(params: UpdateMetadataParams): Promise<UpdateMetadataResponse>;
}