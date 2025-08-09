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
import { ImageModel, DeletedImageInfo } from '@/types/models';

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

    const response = await apiClient.getWithTransform<ImageModel[]>('/images', { params: finalParams });
    // 假设此端点的服务器响应包含 ImagesListResponse 定义的正确元数据结构
    return response as ImagesListResponse;
  },

  /**
   * 获取单张图片详情
   * GET /api/v1/images/{image_id}
   */
  getImageDetail: (params: GetImageDetailParams): Promise<ImageDetailResponse> => {
    return apiClient.getWithTransform<ImageModel>(`/images/${params.image_id}`);
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

    return apiClient.postWithTransform<ImageModel[]>('/images/upload', formData, {
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

    return apiClient.patchWithTransform<ImageModel>(`/images/${params.image_id}`, formData, {
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
