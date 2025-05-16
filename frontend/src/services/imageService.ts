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
} from '../types/image';
import { ImageModel, DeletedImageInfo } from '../types/models';

const imageService: ImageClient = {
  /**
   * 获取图片列表
   * GET /api/images/
   */
  getImagesList: async (params?: GetImagesListParams): Promise<ImagesListResponse> => {
    const response = await apiClient.getWithTransform<ImageModel[]>('/images', { params });
    // 假设此端点的服务器响应包含 ImagesListResponse 定义的正确元数据结构
    return response as ImagesListResponse;
  },

  /**
   * 获取单张图片详情
   * GET /api/images/{image_id}
   */
  getImageDetail: (params: GetImageDetailParams): Promise<ImageDetailResponse> => {
    return apiClient.getWithTransform<ImageModel>(`/images/${params.image_id}`);
  },

  /**
   * 上传一张或多张图片
   * POST /api/images
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
    }
    if (params.metadata) {
      if (typeof params.metadata === 'string') {
        formData.append('metadata', params.metadata);
      } else { // Record<string, unknown>
        formData.append('metadata', JSON.stringify(params.metadata));
      }
    }

    return apiClient.postWithTransform<ImageModel[]>('/images', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * 更新图片信息
   * PATCH /api/images/{image_id}
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
   * DELETE /api/images/{image_id}
   */
  deleteImage: (params: DeleteImageParams): Promise<DeleteImageResponse> => {
    return apiClient.deleteWithTransform<DeletedImageInfo>(`/images/${params.image_id}`);
  },

  /**
   * 获取图片文件URL
   */
  getImageUrl: (imageId: number | string): string => {
    return `${API_BASE_URL}/images/${imageId}/file`;
  },

  /**
   * 获取图片缩略图URL
   */
  getThumbnailUrl: (imageId: number | string, size?: 'small' | 'medium' | 'large'): string => {
    const thumbSize = size || 'medium';
    return `${API_BASE_URL}/images/${imageId}/thumbnail?size=${thumbSize}`;
  },
};

export default imageService;
