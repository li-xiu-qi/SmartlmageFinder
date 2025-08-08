/**
 * 统一的类型导出文件
 * 集中导出所有模块的类型定义
 */

// 模型类型
export * from './models';
export * from './image';
export * from './search';
export * from './metadata';
export * from './tag';

// 为向后兼容导出别名
export type { ImageModel as ImageDetail } from './models';
export type { SearchImageItem as ImageSearchResult } from './models';
