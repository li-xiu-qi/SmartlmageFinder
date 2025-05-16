// 导入 antd 的 message 组件，用于显示提示信息
import { message } from 'antd';
// 导入当前目录下的类型定义
import { UploadFile, ImageMetadata, SelectableTag, UploadResult, UploadResultItem } from './types';
// 导入标签服务，用于获取标签数据
import tagService from '@/services/tagService';
// 导入AI服务，用于图片分析
import aiService from '@/services/aiService';
// 导入图片服务，用于图片上传
import imageService from '@/services/imageService';
// 导入图片数据模型
import { ImageModel } from '@/types/models';
// 导入AI分析详细程度枚举
import { AnalysisDetailLevel, AIErrorCode, ImageAnalysisData } from '@/types/ai';
import { ApiError, ApiResponse } from '@/types/api';

/**
 * 获取可用标签数据
 * @param setAvailableTags React状态更新函数，用于设置可用标签列表
 */
export const fetchTagsData = async (
  setAvailableTags: React.Dispatch<React.SetStateAction<SelectableTag[]>>
): Promise<void> => {
  try {
    // 调用标签服务获取热门标签，限制数量为100
    const response = await tagService.getPopularTags({ limit: 100 });
    // 如果请求成功且返回了数据
    if (response.status === 'success' && response.data) {
      // 将返回的标签数据转换为 SelectableTag 格式
      const tags = response.data.map(tagInfo => ({ label: tagInfo.tag, value: tagInfo.tag }));
      setAvailableTags(tags);
    } else {
      // 如果请求失败或未返回数据，显示错误提示
      message.error('获取热门标签失败: ' + response.message);
    }
  } catch (error) {
    // 捕获请求过程中的异常，显示错误提示
    const errorMessage = (error as ApiError)?.message || '获取热门标签时发生未知错误';
    message.error(errorMessage);
  }
};

/**
 * AI 分析单个图片
 * @param file 需要分析的 UploadFile 对象
 * @param setAnalyzingFile React状态更新函数，用于设置当前正在分析的文件
 * @param setIsAnalyzing React状态更新函数，用于设置是否正在进行AI分析的状态
 * @param setImageMetadataMap React状态更新函数，用于更新图片元数据映射表
 */
export const analyzeImage = async (
  file: UploadFile,
  setAnalyzingFile: React.Dispatch<React.SetStateAction<UploadFile | null>>,
  setIsAnalyzing: React.Dispatch<React.SetStateAction<boolean>>,
  setImageMetadataMap: React.Dispatch<React.SetStateAction<Record<string, ImageMetadata>>>
): Promise<void> => {
  // 检查文件对象是否存在 originFileObj，这是实际的文件数据
  if (!file.originFileObj) {
    message.error(`文件 ${file.name} 无效，无法进行AI分析。`);
    return;
  }
  // 设置当前正在分析的文件和分析状态
  setAnalyzingFile(file);
  setIsAnalyzing(true);
  try {
    // 调用AI服务上传并分析图片
    const response: ApiResponse<ImageAnalysisData> = await aiService.analyzeUploadImage({
      file: file.originFileObj, // 使用原始 File 对象
      detail: AnalysisDetailLevel.HIGH, // 设置分析详细程度为高
    });
    // 如果AI分析成功且返回了数据
    if (response.status === 'success' && response.data) {
      // 更新对应文件的元数据
      setImageMetadataMap(prev => ({
        ...prev,
        [file.uid]: {
          ...(prev[file.uid] || {}), // 保留已有的其他元数据，如location, event
          title: response.data!.title,       // 更新标题 (使用非空断言，因为 status success 保证 data 不为 null)
          description: response.data!.description, // 更新描述
          tags: response.data!.tags,         // 更新标签
        },
      }));
      message.success(`图片 ${file.name} AI分析完成。`);
    } else {
      // 如果AI分析失败，显示错误提示
      const errorDetails = response.error?.details as Record<string, string> | undefined;
      let errorMessage = response.message;
      if (response.error?.code === AIErrorCode.SERVICE_UNAVAILABLE) {
        errorMessage = 'AI服务不可用，请检查配置。';
      } else if (errorDetails?.reason) {
        errorMessage += `: ${errorDetails.reason}`;
      }
      message.error(`图片 ${file.name} AI分析失败: ${errorMessage}`);
    }
  } catch (error) {
    // 捕获AI分析过程中的异常，显示错误提示
    const errorMessage = (error as ApiError)?.message || `图片 ${file.name} AI分析时发生未知错误`;
    message.error(errorMessage);
  } finally {
    // 无论成功或失败，最后都重置分析状态
    setIsAnalyzing(false);
    setAnalyzingFile(null);
  }
};

/**
 * 批量AI分析图片
 * @param fileList 需要分析的文件列表
 * @param setIsAnalyzing React状态更新函数，用于设置是否正在进行AI分析的状态
 * @param setAnalyzingFile React状态更新函数，用于设置当前正在分析的文件
 * @param setImageMetadataMap React状态更新函数，用于更新图片元数据映射表
 */
export const batchAnalyzeImages = async (
  fileList: UploadFile[],
  setIsAnalyzing: React.Dispatch<React.SetStateAction<boolean>>,
  setAnalyzingFile: React.Dispatch<React.SetStateAction<UploadFile | null>>,
  setImageMetadataMap: React.Dispatch<React.SetStateAction<Record<string, ImageMetadata>>>
): Promise<void> => {
  setIsAnalyzing(true); // 开始批量分析，设置状态
  // 遍历文件列表，对每个文件进行AI分析
  for (const file of fileList) {
    // 通常AI分析在上传前，或者对已选择的文件进行
    // 此处简单处理，未考虑文件状态 file.status !== 'done'，因为AI分析通常独立于上传状态
    // 注意：内部setIsAnalyzing会被analyzeImage函数覆盖，这里传递一个空函数或不更新setIsAnalyzing，由analyzeImage管理单个文件分析状态
    await analyzeImage(file, setAnalyzingFile, () => {}, setImageMetadataMap);
  }
  setIsAnalyzing(false); // 所有文件分析完成，重置状态
  message.success('所有选定图片的批量AI分析已完成。');
};

/**
 * 上传图片
 * @param fileList 需要上传的文件列表
 * @param imageMetadataMap 包含各文件元数据的映射表
 * @param _commonSettings 通用设置 (参数前加下划线表示当前未使用，以消除 lint 警告)
 * @param setUploading React状态更新函数，用于设置是否正在上传的状态
 * @param setUploadProgress React状态更新函数，用于设置上传进度
 * @param setUploadResult React状态更新函数，用于设置上传结果
 * @param setHasUploaded React状态更新函数，用于标记是否已执行过上传操作
 */
export const uploadImages = async (
  fileList: UploadFile[],
  imageMetadataMap: Record<string, ImageMetadata>,
  _commonSettings: { generateMetadata: boolean }, // 标记为未使用
  setUploading: React.Dispatch<React.SetStateAction<boolean>>,
  setUploadProgress: React.Dispatch<React.SetStateAction<number>>,
  setUploadResult: React.Dispatch<React.SetStateAction<UploadResult | null>>,
  setHasUploaded: React.Dispatch<React.SetStateAction<boolean>>
): Promise<void> => {
  setUploading(true);    // 开始上传，设置状态
  setUploadProgress(0);  // 初始化上传进度
  const totalFiles = fileList.length; // 总文件数
  let uploadedCount = 0; // 已处理文件计数（包括成功和失败）
  const results: UploadResultItem[] = []; // 存储每个文件的上传结果

  // 遍历文件列表进行上传
  for (const file of fileList) {
    // 检查文件对象是否有效
    if (!file.originFileObj) {
      results.push({
        id: file.uid,
        fileName: file.name,
        success: false,
        message: '无效的文件对象'
      });
      uploadedCount++;
      setUploadProgress(Math.round((uploadedCount / totalFiles) * 100));
      continue; // 处理下一个文件
    }

    // 获取当前文件的元数据
    const metadata = imageMetadataMap[file.uid] || {};
    try {
      // 调用图片服务上传图片
      // imageService.uploadImages 期望参数是一个包含 File 对象的数组
      // 此处为每个文件单独调用上传服务，符合逐个处理并反馈进度的场景
      const response: ApiResponse<ImageModel[]> = await imageService.uploadImages({
        files: [file.originFileObj], // 将单个文件包装在数组中
        title: metadata.title,       // 图片标题
        description: metadata.description, // 图片描述
        tags: metadata.tags,         // 图片标签
        // metadata: { location: metadata.location, event: metadata.event } // 可选：传递其他自定义元数据
      });

      // 处理上传响应
      if (response.status === 'success' && response.data && response.data.length > 0) {
        // 上传成功
        results.push({
          id: file.uid,
          fileName: file.name,
          success: true,
          image: response.data[0] as ImageModel, // 假设API总是返回一个包含已上传图片信息的数组
        });
      } else {
        // 上传失败（API层面）
        results.push({
          id: file.uid,
          fileName: file.name,
          success: false,
          message: response.message || '上传失败'
        });
      }
    } catch (error) {
      // 上传过程中发生异常
      results.push({
        id: file.uid,
        fileName: file.name,
        success: false,
        message: (error as ApiError)?.message || '上传时发生未知错误'
      });
    }
    uploadedCount++; // 更新已处理文件计数
    // 更新上传进度条
    setUploadProgress(Math.round((uploadedCount / totalFiles) * 100));
  }

  // 统计上传结果
  const successCount = results.filter(r => r.success).length;
  // 设置整体上传结果
  setUploadResult({
    items: results,
    overallStatus: successCount === totalFiles ? 'success' : (successCount === 0 ? 'failure' : 'partial'),
    successCount,
    failureCount: totalFiles - successCount,
  });
  setUploading(false);  // 上传结束，重置状态
  setHasUploaded(true); // 标记已执行过上传
  message.info('图片上传处理完成。');
};
