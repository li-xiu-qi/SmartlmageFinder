import apiClient from './apiClient';
import { 
  ImageAnalysisResponse, 
  ImageAnalysisClient, 
  UploadImageAnalysisRequestParams, 
  ExistingImageAnalysisFormParams,
  ImageAnalysisServiceConfig,
  AnalysisDetailLevel,
  ImageAnalysisData
} from '@/types/imageAnalysis';

/**
 * 图片分析服务实现
 * 实现ImageAnalysisClient接口
 */
const imageAnalysisService: ImageAnalysisClient = {
  /**
   * 分析上传图片
   * POST /api/v1/ai/analyze-upload-image
   * @param params 包含图片文件和分析详细程度的请求参数
   * @returns 分析结果的 Promise
   */
  analyzeUploadImage: async (
    params: UploadImageAnalysisRequestParams
  ): Promise<ImageAnalysisResponse> => {
    const formData = new FormData();
    formData.append('file', params.file);
    formData.append('detail', params.detail || AnalysisDetailLevel.LOW);
    
    const response = await apiClient.postWithTransform<ImageAnalysisData>('/ai/analyze-upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 90000  // 图片分析需要更长时间，设置90秒超时
    });
    
    return response as ImageAnalysisResponse;
  },

  /**
   * 分析已有图片
   * POST /api/v1/ai/analyze-image-id/{image_id}
   * @param imageId 图片ID
   * @param params 可选的分析参数
   * @returns 分析结果的 Promise
   */
  analyzeExistingImage: async (
    imageId: string | number,
    params?: ExistingImageAnalysisFormParams
  ): Promise<ImageAnalysisResponse> => {
    const formData = new FormData();
    formData.append('detail', params?.detail || AnalysisDetailLevel.LOW);
    
    const response = await apiClient.postWithTransform<ImageAnalysisData>(`/ai/analyze-image-id/${imageId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    return response as ImageAnalysisResponse;
  },
  
  /**
   * 获取图片分析服务配置状态
   * GET /api/v1/ai/service-status
   * @returns 服务配置信息的 Promise
   */
  getServiceStatus: async (): Promise<ImageAnalysisServiceConfig> => {
    const response = await apiClient.getWithTransform<ImageAnalysisServiceConfig>('/ai/service-status');
    
    if (response.status === 'success' && response.data) {
      return response.data;
    }
    
    // 如果请求失败，返回默认配置
    return {
      isAvailable: false,
      configuredModels: [],
      apiProvider: '未知'
    };
  }
};

export default imageAnalysisService;
