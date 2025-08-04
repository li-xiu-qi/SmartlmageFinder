// 导入 antd 的 message 组件，用于显示提示信息
import { message } from 'antd';
// 导入当前目录下的类型定义
import { UploadFile, ImageMetadata, SelectableTag, UploadResult, UploadResultItem, AnalysisMode } from './types';
// 导入标签服务，用于获取标签数据
import tagService from '@/services/tagService';
// 导入AI服务，用于图片分析
import imageAnalysisService from '@/services/imageAnalysisService';
// 导入图片服务，用于图片上传
import imageService from '@/services/imageService';
// 导入图片数据模型
import { ImageModel } from '@/types/models';
// 导入AI分析详细程度枚举
import { AnalysisDetailLevel, ImageAnalysisErrorCode } from '@/types/imageAnalysis';
import { ApiError } from '@/types/api';

// 并发设置选项接口
interface ConcurrencyOptions {
  concurrent: boolean;    // 是否启用并发分析
  concurrentLimit: number; // 并发限制数量
  mode?: AnalysisMode;    // 分析模式（可选，默认分析全部）
}

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
 * 根据分析模式过滤需要分析的文件
 * @param fileList 所有文件列表
 * @param imageMetadataMap 图片元数据映射
 * @param mode 分析模式
 * @returns 过滤后的文件列表
 */
const filterFilesForAnalysis = (
  fileList: UploadFile[],
  imageMetadataMap: Record<string, ImageMetadata>,
  mode: AnalysisMode = AnalysisMode.ALL
): UploadFile[] => {
  if (mode === AnalysisMode.ALL) {
    return fileList;
  }

  if (mode === AnalysisMode.UNANALYZED_ONLY) {
    return fileList.filter(file => {
      const metadata = imageMetadataMap[file.uid];
      // 如果没有元数据，或者标题、描述、标签都为空，则认为未分析
      return !metadata || (!metadata.title && !metadata.description && metadata.tags.length === 0);
    });
  }

  return fileList;
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
    // 调用图片分析服务上传并分析图片
    const response = await imageAnalysisService.analyzeUploadImage({
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
          title: response.data.title,       // 更新标题
          description: response.data.description, // 更新描述
          tags: response.data.tags,         // 更新标签
        },
      }));
      message.success(`图片 ${file.name} 分析完成。`);
    } else {
      // 如果图片分析失败，显示错误提示
      const errorDetails = response.error?.details as Record<string, string> | undefined;
      let errorMessage = response.message || '未知错误';
      if (response.error?.code === ImageAnalysisErrorCode.SERVICE_UNAVAILABLE) {
        errorMessage = '图片分析服务不可用，请检查配置。';
      } else if (errorDetails?.reason) {
        errorMessage += `: ${errorDetails.reason}`;
      }
      message.error(`图片 ${file.name} 分析失败: ${errorMessage}`);
    }
  } catch (error) {
    // 捕获图片分析过程中的异常，显示错误提示
    const errorMessage = (error as ApiError)?.message || `图片 ${file.name} 分析时发生未知错误`;
    message.error(errorMessage);
    console.error('图片分析错误:', error);
  } finally {
    // 无论成功或失败，最后都重置分析状态
    setIsAnalyzing(false);
    setAnalyzingFile(null);
  }
};

/**
 * 分析单个文件的内部函数（不更新全局状态）
 * @param file 需要分析的文件
 * @param setImageMetadataMap 元数据更新函数
 * @returns Promise<boolean> 分析是否成功
 */
const analyzeSingleFile = async (
  file: UploadFile,
  setImageMetadataMap: React.Dispatch<React.SetStateAction<Record<string, ImageMetadata>>>
): Promise<boolean> => {
  // 检查文件对象是否存在 originFileObj
  if (!file.originFileObj) {
    message.error(`文件 ${file.name} 无效，无法进行AI分析。`);
    return false;
  }

  try {
    // 调用图片分析服务上传并分析图片
    const response = await imageAnalysisService.analyzeUploadImage({
      file: file.originFileObj,
      detail: AnalysisDetailLevel.HIGH,
    });

    // 如果图片分析成功且返回了数据
    if (response.status === 'success' && response.data) {
      // 更新对应文件的元数据
      setImageMetadataMap(prev => ({
        ...prev,
        [file.uid]: {
          ...(prev[file.uid] || {}),
          title: response.data.title,
          description: response.data.description,
          tags: response.data.tags,
        },
      }));
      message.success(`图片 ${file.name} 分析完成。`);
      return true;
    } else {
      // 如果图片分析失败，显示错误提示
      const errorDetails = response.error?.details as Record<string, string> | undefined;
      let errorMessage = response.message || '未知错误';
      if (response.error?.code === ImageAnalysisErrorCode.SERVICE_UNAVAILABLE) {
        errorMessage = '图片分析服务不可用，请检查配置。';
      } else if (errorDetails?.reason) {
        errorMessage += `: ${errorDetails.reason}`;
      }
      message.error(`图片 ${file.name} 分析失败: ${errorMessage}`);
      return false;
    }
  } catch (error) {
    // 捕获AI分析过程中的异常
    const errorMessage = (error as ApiError)?.message || `图片 ${file.name} AI分析时发生未知错误`;
    message.error(errorMessage);
    console.error('批量AI分析单张图片错误:', error);
    return false;
  }
};

/**
 * 串行批量AI分析图片（原有逻辑）
 * @param fileList 需要分析的文件列表
 * @param setAnalyzingFile 当前分析文件更新函数
 * @param setImageMetadataMap 元数据更新函数
 */
const batchAnalyzeSequential = async (
  fileList: UploadFile[],
  setAnalyzingFile: React.Dispatch<React.SetStateAction<UploadFile | null>>,
  setImageMetadataMap: React.Dispatch<React.SetStateAction<Record<string, ImageMetadata>>>
): Promise<void> => {
  try {
    // 遍历文件列表，对每个文件进行AI分析
    for (const file of fileList) {
      // 设置当前正在分析的文件
      setAnalyzingFile(file);

      // 分析单个文件
      await analyzeSingleFile(file, setImageMetadataMap);
    }

    message.success('所有选定图片的批量AI分析已完成。');
  } catch (error) {
    // 捕获整个批处理过程中的异常
    const errorMessage = (error as ApiError)?.message || '批量AI分析时发生未知错误';
    message.error(errorMessage);
    console.error('批量AI分析总体错误:', error);
  }
};

/**
 * 并发批量AI分析图片
 * @param fileList 需要分析的文件列表
 * @param setAnalyzingFile 当前分析文件更新函数
 * @param setImageMetadataMap 元数据更新函数
 * @param concurrentLimit 并发限制数量
 */
const batchAnalyzeConcurrent = async (
  fileList: UploadFile[],
  setAnalyzingFile: React.Dispatch<React.SetStateAction<UploadFile | null>>,
  setImageMetadataMap: React.Dispatch<React.SetStateAction<Record<string, ImageMetadata>>>,
  concurrentLimit: number
): Promise<void> => {
  try {
    const totalFiles = fileList.length;
    let processedCount = 0;
    let successCount = 0;

    // 分批处理文件
    for (let i = 0; i < totalFiles; i += concurrentLimit) {
      const batch = fileList.slice(i, i + concurrentLimit);

      // 设置当前批次的第一个文件为当前分析文件（用于显示）
      if (batch.length > 0) {
        setAnalyzingFile(batch[0]);
      }

      // 并行处理当前批次
      const batchPromises = batch.map(file => analyzeSingleFile(file, setImageMetadataMap));
      const batchResults = await Promise.all(batchPromises);

      // 统计结果
      const batchSuccessCount = batchResults.filter(result => result).length;
      processedCount += batch.length;
      successCount += batchSuccessCount;

      // 显示进度信息
      message.info(`已处理 ${processedCount}/${totalFiles} 张图片，成功 ${successCount} 张`);
    }

    message.success(`批量AI分析完成！共处理 ${totalFiles} 张图片，成功分析 ${successCount} 张。`);
  } catch (error) {
    // 捕获整个并发批处理过程中的异常
    const errorMessage = (error as ApiError)?.message || '并发批量AI分析时发生未知错误';
    message.error(errorMessage);
    console.error('并发批量AI分析总体错误:', error);
  }
};

/**
 * 批量AI分析图片（支持并发控制）
 * @param fileList 需要分析的文件列表
 * @param setIsAnalyzing React状态更新函数，用于设置是否正在进行AI分析的状态
 * @param setAnalyzingFile React状态更新函数，用于设置当前正在分析的文件
 * @param setImageMetadataMap React状态更新函数，用于更新图片元数据映射表
 * @param options 并发控制选项
 */
/**
 * 批量AI分析图片（支持并发控制和分析模式）
 * @param fileList 需要分析的文件列表
 * @param setIsAnalyzing React状态更新函数，用于设置是否正在进行AI分析的状态
 * @param setAnalyzingFile React状态更新函数，用于设置当前正在分析的文件
 * @param setImageMetadataMap React状态更新函数，用于更新图片元数据映射表
 * @param imageMetadataMap 当前的图片元数据映射
 * @param options 并发控制选项
 */
export const batchAnalyzeImages = async (
  fileList: UploadFile[],
  setIsAnalyzing: React.Dispatch<React.SetStateAction<boolean>>,
  setAnalyzingFile: React.Dispatch<React.SetStateAction<UploadFile | null>>,
  setImageMetadataMap: React.Dispatch<React.SetStateAction<Record<string, ImageMetadata>>>,
  imageMetadataMap: Record<string, ImageMetadata>,
  options: ConcurrencyOptions = { concurrent: false, concurrentLimit: 3 }
): Promise<void> => {
  // 根据分析模式过滤需要分析的文件
  const filesToAnalyze = filterFilesForAnalysis(fileList, imageMetadataMap, options.mode);

  if (filesToAnalyze.length === 0) {
    message.warning('没有需要分析的图片');
    return;
  }

  // 开始批量分析，设置全局分析状态
  setIsAnalyzing(true);

  const modeText = options.mode === AnalysisMode.UNANALYZED_ONLY ? '未分析的' : '所有';
  message.info(`开始分析${modeText}图片，共${filesToAnalyze.length}张`);

  try {
    if (options.concurrent && options.concurrentLimit > 1) {
      // 使用并发处理
      message.info(`开始并发批量AI分析，并发数量：${options.concurrentLimit}`);
      await batchAnalyzeConcurrent(
        filesToAnalyze,
        setAnalyzingFile,
        setImageMetadataMap,
        options.concurrentLimit
      );
    } else {
      // 使用串行处理
      message.info('开始串行批量AI分析');
      await batchAnalyzeSequential(
        filesToAnalyze,
        setAnalyzingFile,
        setImageMetadataMap
      );
    }
  } finally {
    // 无论成功或失败，最后都重置分析状态
    setIsAnalyzing(false);
    setAnalyzingFile(null);
  }
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
    const metadata = imageMetadataMap[file.uid] || { title: '', description: '', tags: [] };
    try {
      // 调用图片服务上传图片
      // imageService.uploadImages 期望参数是一个包含 File 对象的数组
      // 此处为每个文件单独调用上传服务，符合逐个处理并反馈进度的场景
      const response = await imageService.uploadImages({
        files: [file.originFileObj], // 将单个文件包装在数组中
        title: metadata.title || '',       // 图片标题，确保不为undefined
        description: metadata.description || '', // 图片描述，确保不为undefined
        tags: metadata.tags || [],         // 图片标签，确保不为undefined
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
      console.error('上传图片错误:', error);
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
