/**
 * 搜索页面常量定义
 */
import { SearchType, VectorSearchTarget } from '@/types/search';

/**
 * 搜索类型选项
 */
export const SEARCH_TYPES = [
  { value: SearchType.TITLE, label: '仅标题' },
  { value: SearchType.DESCRIPTION, label: '仅描述' },
  { value: SearchType.BOTH, label: '标题+描述' },
  { value: SearchType.VECTOR, label: '向量搜索' },
  { value: SearchType.HYBRID, label: '混合搜索' }
];

/**
 * 文本搜索类型选项
 */
export const TEXT_SEARCH_TYPES = [
  { value: SearchType.TITLE, label: '仅标题' },
  { value: SearchType.DESCRIPTION, label: '仅描述' },
  { value: SearchType.BOTH, label: '标题+描述' }
];

/**
 * 高级搜索类型选项
 */
export const ADVANCED_SEARCH_TYPES = [
  { value: SearchType.VECTOR, label: '向量搜索' },
  { value: SearchType.HYBRID, label: '混合搜索' }
];

/**
 * 向量搜索目标选项
 */
export const VECTOR_SEARCH_TARGETS = [
  { value: VectorSearchTarget.TITLE, label: '标题向量' },
  { value: VectorSearchTarget.DESCRIPTION, label: '描述向量' },
  { value: VectorSearchTarget.IMAGE, label: '图像向量' }
];

/**
 * 图像搜索目标选项
 */
export const IMAGE_SEARCH_TARGETS = [
  { value: VectorSearchTarget.IMAGE, label: '图像向量' },
  { value: VectorSearchTarget.TITLE, label: '标题向量' },
  { value: VectorSearchTarget.DESCRIPTION, label: '描述向量' }
];

/**
 * 默认分页大小
 */
export const DEFAULT_PAGE_SIZE = 20;

/**
 * 文件上传配置
 */
export const UPLOAD_CONFIG = {
  MAX_FILE_SIZE: 100, // 最大文件大小(MB)
  ACCEPTED_TYPES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
};
