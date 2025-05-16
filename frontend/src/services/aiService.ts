import apiClient from './apiClient';
import { 
  ImageAnalysisResponse, 
  AIAnalysisClient, 
  UploadImageAnalysisRequestParams, 
  ExistingImageAnalysisFormParams,
  AIServiceConfig,
  AnalysisDetailLevel,
  ImageAnalysisData
} from '@/types/ai';

/**
 * AI分析服务实现
 * 实现AIAnalysisClient接口
 */
const aiService: AIAnalysisClient = {
  /**
   * 分析上传图片
   * POST /api/ai/analyze-upload-image
   * @param params 包含图片文件和分析详细程度的请求参数
   * @returns 分析结果的 Promise
   */  analyzeUploadImage: (
    params: UploadImageAnalysisRequestParams
  ): Promise<ImageAnalysisResponse> => {
    const formData = new FormData();
    formData.append('file', params.file);
    formData.append('detail', params.detail || AnalysisDetailLevel.LOW);
    
    return apiClient.postWithTransform<ImageAnalysisResponse>('/ai/analyze-upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },

  /**
   * 分析已有图片
   * POST /api/ai/analyze-image-id/{image_id}
   * @param imageId 图片ID
   * @param params 可选的分析参数
   * @returns 分析结果的 Promise
   */  analyzeExistingImage: (
    imageId: string | number,
    params?: ExistingImageAnalysisFormParams
  ): Promise<ImageAnalysisResponse> => {
    const formData = new FormData();
    formData.append('detail', params?.detail || AnalysisDetailLevel.LOW);
    
    return apiClient.postWithTransform<ImageAnalysisData>(`/ai/analyze-image-id/${imageId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  /**
   * 获取AI服务配置状态
   * GET /api/ai/service-status
   * @returns 服务配置信息的 Promise
   */
  getServiceStatus: (): Promise<AIServiceConfig> => {
    return apiClient.get('/ai/service-status');
  }
};

export default aiService;
