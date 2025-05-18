// filepath: c:\Users\k\Documents\project\programming_project\python_project\importance\SmartImageFinder\frontend\src\services\metadataService.ts
/**
 * 元数据管理服务
 * 负责与后端元数据相关的API进行交互
 */

import apiClient from './apiClient';
import { UpdateMetadataParams, UpdateMetadataResponse, MetadataClient } from '@/types/metadata';
import { ImageModel } from '@/types/models';

class MetadataService implements MetadataClient {
  /**
   * 更新图片的元数据
   * @param params 包含 image_id 和 metadata 的对象
   * @returns Promise<UpdateMetadataResponse>
   */
  async updateMetadata(params: UpdateMetadataParams): Promise<UpdateMetadataResponse> {
    const { image_id, metadata } = params;
    // 后端期望的请求体格式是 { "metadata": { ... } }
    const payload = { metadata };
    return apiClient.putWithTransform<ImageModel>(
      `/metadata/${image_id}/update`,
      payload
    );
  }
}

const metadataService = new MetadataService();

export default metadataService;
