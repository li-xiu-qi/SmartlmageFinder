import type { ApiResponse } from '@/types';

/**
 * 校验分页元数据是否存在并结构完整
 */
export function validatePagination<T>(resp: ApiResponse<T>, context: string): void {
  const pagination = (resp as any)?.metadata?.pagination as any;
  if (!pagination) {
    throw new Error(`${context}: 缺少 metadata.pagination`);
  }
  const required = ['page', 'page_size', 'total_items', 'total_pages'];
  for (const k of required) {
    if (pagination[k] === undefined || pagination[k] === null) {
      throw new Error(`${context}: pagination.${k} 缺失`);
    }
  }
}

/**
 * 为搜索结果补充统一的 SearchMetadata（total_results / execution_time_ms）
 * 后端当前只返回 metadata.pagination，我们派生 total_results；execution_time_ms 暂缺用0占位
 */
export function enrichSearchMetadata<T>(resp: ApiResponse<T[]>): ApiResponse<T[]> {
  try {
    const pagination: any = (resp as any)?.metadata?.pagination;
    if (pagination && (resp as any).metadata) {
      (resp as any).metadata.total_results = pagination.total_items;
      if ((resp as any).metadata.execution_time_ms === undefined) {
        (resp as any).metadata.execution_time_ms = 0;
      }
    }
  } catch {
    // 忽略补充失败，不中断主流程
  }
  return resp;
}
