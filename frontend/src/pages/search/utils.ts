/**
 * 搜索页面工具函数
 */
import { VectorSearchTarget } from '@/types/search';

/**
 * 将URL参数中的标签字符串转换为标签数组
 * @param tagsParam 逗号分隔的标签字符串
 * @returns 标签数组
 */
export const parseTagsFromParam = (tagsParam: string | null): string[] => {
  if (!tagsParam) return [];
  return tagsParam.split(',').filter(Boolean);
};

/**
 * 将标签数组转换为URL参数字符串
 * @param tags 标签数组
 * @returns 逗号分隔的标签字符串
 */
export const formatTagsForParam = (tags: string[]): string => {
  return tags.join(',');
};


// 已移除 mapToApiVectorType：直接在调用处使用枚举


/**
 * 获取向量搜索目标数组
 * @param targetValues 目标值数组
 * @returns 向量搜索目标数组
 */
export const getVectorSearchTargets = (targetValues: string[]): VectorSearchTarget[] => {
  const map: Record<string, VectorSearchTarget> = {
    'title': VectorSearchTarget.TITLE,
    'description': VectorSearchTarget.DESCRIPTION,
    'image': VectorSearchTarget.IMAGE
  };
  
  return targetValues.map(value => map[value] || VectorSearchTarget.IMAGE);
};

/**
 * 验证上传的图片文件
 * @param file 图片文件
 * @param maxSize 最大文件大小（MB）
 * @returns 验证结果
 */
export const validateImageFile = (file: File, maxSize: number = 10): { valid: boolean; message?: string } => {
  const isImage = file.type.startsWith('image/');
  if (!isImage) {
    return { valid: false, message: '请上传图片文件！' };
  }
  
  const isLt10M = file.size / 1024 / 1024 < maxSize;
  if (!isLt10M) {
    return { valid: false, message: `图片必须小于 ${maxSize}MB！` };
  }
  
  return { valid: true };
};

/**
 * 从文件获取图片预览URL
 * @param file 图片文件
 * @returns 预览URL Promise
 */
export const getImagePreviewUrl = (file: File): Promise<string> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
  });
};
