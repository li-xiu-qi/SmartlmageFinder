/**
 * 搜索页面工具函数
 */
import { SearchType, VectorType, VectorSearchTarget } from '@/types/search';

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

/**
 * 文本搜索类型转换为API搜索类型
 * @param searchType 前端搜索类型
 * @returns API搜索类型
 */
export const mapToApiSearchType = (searchType: string): SearchType => {
  const map: Record<string, SearchType> = {
    'title': SearchType.TITLE,
    'description': SearchType.DESCRIPTION,
    'both': SearchType.BOTH,
    'combined': SearchType.BOTH,
    'vector': SearchType.VECTOR
    // 'multi'和'hybrid'类型已不再支持
  };
  
  return map[searchType] || SearchType.BOTH;
};

/**
 * 向量类型转换为API向量类型
 * @param vectorType 前端向量类型
 * @returns API向量类型
 */
export const mapToApiVectorType = (vectorType: string): VectorType => {
  const map: Record<string, VectorType> = {
    'title': VectorType.TITLE,
    'description': VectorType.DESCRIPTION,
    'image': VectorType.IMAGE
  };
  
  return map[vectorType] || VectorType.IMAGE;
};

/**
 * 检查搜索类型是否是高级搜索（向量或多维）
 * @param searchType 搜索类型
 * @returns 是否是高级搜索
 */
export const isAdvancedSearch = (searchType: string): boolean => {
  return ['vector'].includes(searchType);
};

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
