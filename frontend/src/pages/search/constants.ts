/**
 * 搜索页面常量定义
 */
import { VectorSearchTarget, VectorType } from '@/types/search';

// 已移除搜索类型切换，仅保留向量/模糊/以图在不同 Tab 中

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
 * 向量类型选项
 */
export const VECTOR_TYPES = [
  { value: VectorType.TITLE, label: '标题向量' },
  { value: VectorType.DESCRIPTION, label: '描述向量' },
  { value: VectorType.IMAGE, label: '图像向量' }
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
