/**
 * SmartImageFinder 图片分析功能相关类型定义
 * 基于图片分析 API 文档定义
 */

import { ApiResponse } from './api';

/**
 * 图片分析结果数据结构
 * 与后端 /api/ai/analyze-upload-image 和 /api/ai/analyze-image-id/{image_id} 接口的返回格式一致
 */
export interface ImageAnalysisData {
  title: string;         // AI 生成的图片标题
  description: string;   // AI 生成的图片描述
  tags: string[];        // AI 推荐的标签列表
}

// 为了兼容现有代码，保留GeneratedContent别名
export type GeneratedContent = ImageAnalysisData;

/**
 * 图片分析元数据
 */
export interface ImageAnalysisMetadata {
  model: string;         // 使用的 AI 模型名称
  time_ms: number;       // 处理时间（毫秒）
}

/**
 * 分析图片详细程度枚举
 */
export enum AnalysisDetailLevel {
  LOW = 'low',    // 低详细度：简短标题、简洁描述、约5-7个标签
  HIGH = 'high'   // 高详细度：详细标题、详细描述（含色彩构图分析）、约10-15个标签
}

/**
 * 图片分析错误代码枚举
 */
export enum ImageAnalysisErrorCode {
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',   // 图片分析服务不可用，可能由于API密钥未配置或无效
  AI_PROCESSING_ERROR = 'AI_PROCESSING_ERROR',   // AI处理过程中发生错误
  IMAGE_ANALYSIS_ERROR = 'IMAGE_ANALYSIS_ERROR'  // 图片分析错误，如图片不存在或文件损坏
}

/**
 * 上传图片分析请求参数
 */
export interface UploadImageAnalysisRequestParams {
  file: File;                           // 要分析的图片文件
  detail?: AnalysisDetailLevel;         // 分析详细程度，默认为 LOW
}

/**
 * 分析已有图片请求参数 (URL路径中的参数)
 */
export interface ExistingImageAnalysisPathParams {
  image_id: string | number;            // 要分析的图片ID
}

/**
 * 分析已有图片请求参数 (表单参数)
 */
export interface ExistingImageAnalysisFormParams {
  detail?: AnalysisDetailLevel;         // 分析详细程度，默认为 LOW
}

/**
 * 图片分析响应类型
 */
export type ImageAnalysisResponse = ApiResponse<ImageAnalysisData> & {
  metadata: ImageAnalysisMetadata;
};

/**
 * 图片分析服务配置
 */
export interface ImageAnalysisServiceConfig {
  isAvailable: boolean;                  // 图片分析服务是否可用
  configuredModels: string[];            // 已配置的模型列表
  apiProvider: string;                   // API 提供者 (如 "OpenAI")
}

/**
 * 图片分析服务客户端接口
 */
export interface ImageAnalysisClient {
  /**
   * 上传并分析新图片
   * @param params 包含图片文件和分析详细程度的请求参数
   * @returns 分析结果的 Promise
   */
  analyzeUploadImage(params: UploadImageAnalysisRequestParams): Promise<ImageAnalysisResponse>;
  
  /**
   * 分析已有图片
   * @param imageId 图片ID
   * @param params 可选的分析参数
   * @returns 分析结果的 Promise
   */
  analyzeExistingImage(imageId: string | number, params?: ExistingImageAnalysisFormParams): Promise<ImageAnalysisResponse>;
  
  /**
   * 检查图片分析服务状态
   * @returns 服务配置信息的 Promise
   */
  getServiceStatus(): Promise<ImageAnalysisServiceConfig>;
}