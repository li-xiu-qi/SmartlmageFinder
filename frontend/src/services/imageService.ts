import apiClient, { API_BASE_URL } from './apiClient';
import {
  ImageClient,
  GetImagesListParams,
  ImagesListResponse,
  GetImageDetailParams,
  ImageDetailResponse,
  UploadImageParams,
  UploadImagesResponse,
  UpdateImageParams,
  UpdateImageResponse,
  DeleteImageParams,
  DeleteImageResponse,
  BatchDeleteImageParams,
  BatchDeleteImageResponse,
} from '@/types/image';
import { ImageDetail, DeletedImageInfo } from '@/types/models';

const imageService: ImageClient = {
  /**
   * 获取图片列表
   * GET /api/v1/images/
   */
  getImagesList: async (params?: GetImagesListParams): Promise<ImagesListResponse> => {
    // 将 tags 统一为逗号分隔字符串，防止 axios 序列化为 tags[]
    let finalParams: Record<string, any> | undefined = undefined;
    if (params) {
      const { tags, ...rest } = params;
      finalParams = { ...rest } as Record<string, any>;
      if (Array.isArray(tags)) {
        finalParams.tags = tags.join(',');
      } else if (typeof tags === 'string') {
        finalParams.tags = tags;
      }
    }

    const apiResp = await apiClient.getWithTransform<ImageDetail[]>('/images', { params: finalParams });
    const pagination = (apiResp.metadata as any)?.pagination;
    // 严格校验：后端 images.py 使用 ResponseModel.paginated_response 保证提供 pagination
    if (!pagination || typeof pagination !== 'object') {
      throw new Error('服务器响应缺少 pagination 元数据');
    }
    // 进一步字段类型校验（若不合法直接抛错，便于尽早发现后端契约偏差）
    const requiredKeys: Array<keyof typeof pagination> = ['page', 'page_size', 'total_items', 'total_pages'];
    for (const k of requiredKeys) {
      if (typeof pagination[k] !== 'number' || Number.isNaN(pagination[k])) {
        throw new Error(`服务器 pagination 字段无效: ${String(k)}`);
      }
    }
    return apiResp as ImagesListResponse;
  },

  /**
   * 获取单张图片详情
   * GET /api/v1/images/{image_id}
   */
  getImageDetail: (params: GetImageDetailParams): Promise<ImageDetailResponse> => {
  return apiClient.getWithTransform<ImageDetail>(`/images/${params.image_id}`);
  },

  /**
   * 上传一张或多张图片
   * POST /api/v1/images
   */
  uploadImages: (params: UploadImageParams): Promise<UploadImagesResponse> => {
    const formData = new FormData();

    if (params.files instanceof FileList) {
      for (let i = 0; i < params.files.length; i++) {
        formData.append('files', params.files[i]);
      }
    } else if (Array.isArray(params.files)) { // File[]
      params.files.forEach(file => {
        formData.append('files', file);
      });
    }

    if (params.title !== undefined) {
      formData.append('title', params.title);
    }
    if (params.description !== undefined) {
      formData.append('description', params.description);
    }
    if (params.tags) {
      if (typeof params.tags === 'string') {
        formData.append('tags', params.tags);
      } else { // string[]
        formData.append('tags', JSON.stringify(params.tags));
      }
    }    if (params.metadata) {
      if (typeof params.metadata === 'string') {
        formData.append('metadata', params.metadata);
      } else { // Record<string, unknown>
        formData.append('metadata', JSON.stringify(params.metadata));
      }
    }

  return apiClient.postWithTransform<ImageDetail[]>('/images/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000,  // 图片上传需要更长时间，设置2分钟超时
    });
  },

  /**
   * 更新图片信息
   * PATCH /api/v1/images/{image_id}
   */
  updateImage: (params: UpdateImageParams): Promise<UpdateImageResponse> => {
    const formData = new FormData();

    if (params.title !== undefined) {
      formData.append('title', params.title);
    }
    if (params.description !== undefined) {
      formData.append('description', params.description);
    }
    if (params.tags) {
      if (typeof params.tags === 'string') {
        formData.append('tags', params.tags);
      } else { // string[]
        formData.append('tags', JSON.stringify(params.tags));
      }
    }
    if (params.metadata) {
      if (typeof params.metadata === 'string') {
        formData.append('metadata', params.metadata);
      } else { // Record<string, unknown>
        formData.append('metadata', JSON.stringify(params.metadata));
      }
    }

  return apiClient.patchWithTransform<ImageDetail>(`/images/${params.image_id}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * 删除图片
   * DELETE /api/v1/images/{image_id}
   */
  deleteImage: (params: DeleteImageParams): Promise<DeleteImageResponse> => {
    return apiClient.deleteWithTransform<DeletedImageInfo>(`/images/${params.image_id}`);
  },

  /**
   * 批量删除图片
   * DELETE /api/v1/images/batch
   */
  batchDeleteImages: async (params: BatchDeleteImageParams): Promise<BatchDeleteImageResponse> => {
    // 确保所有ID都是数字类型，因为后端期望 List[int]
    const imageIds = params.image_ids.map(id => typeof id === 'string' ? parseInt(id, 10) : id);

    console.log('批量删除请求参数:', { image_ids: imageIds });
    console.log('请求URL:', '/images/batch');

    // 使用带有数据的DELETE请求
    const response = await apiClient.delete('/images/batch', {
      data: { image_ids: imageIds },
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('批量删除响应:', response);

    // 直接返回响应数据，因为后端已经返回了正确的格式
    return response.data;
  },

  /**
   * 获取图片文件URL
   */
  // 改为直接使用后端返回的 public_url，不再拼接 /file 或 /thumbnail
  getImageUrl: (imageId: number | string): string => {
    return `${API_BASE_URL}/images/${imageId}`; // 若仍需要详情，可再取 public_url 字段
  },
};

export default imageService;
