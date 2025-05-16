/**
 * 搜索页面工具函数
 */
import { SearchType } from '@/types/search';

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
 * 格式化权重为逗号分隔的字符串
 * @param weights 权重对象
 * @param modes 模式数组
 * @returns 逗号分隔的权重字符串
 */
export const formatWeights = (weights: {[key: string]: number}, modes: string[]): string => {
  return modes.map(mode => weights[mode] || 0).join(',');
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
    'vector': SearchType.VECTOR,
    'hybrid': SearchType.HYBRID
  };
  
  return map[searchType] || SearchType.BOTH;
};

/**
 * 检查搜索类型是否是高级搜索（向量或混合）
 * @param searchType 搜索类型
 * @returns 是否是高级搜索
 */
export const isAdvancedSearch = (searchType: string): boolean => {
  return ['vector', 'hybrid'].includes(searchType);
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
 * 获取图片预览URL
 * @param file 图片文件
 * @returns 预览URL
 */
export const getImagePreviewUrl = (file: File): Promise<string> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.addEventListener('load', () => resolve(reader.result as string));
    reader.readAsDataURL(file);
  });
};
