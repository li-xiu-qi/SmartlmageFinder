import { useState, useEffect, useCallback } from 'react';
import { systemService } from '@/services/api';
import type { VectorEngineStatus } from '@/types/system';

interface UseVectorCapabilityResult {
  /** 向量功能是否可用 */
  vectorEnabled: boolean;
  /** 完整状态详情 */
  status: VectorEngineStatus | null;
  /** 是否正在加载 */
  loading: boolean;
  /** 错误信息 */
  error: Error | null;
  /** 手动刷新 */
  refresh: () => Promise<void>;
}

/**
 * 向量能力钩子
 *
 * 获取向量引擎状态（驱动 + 模型），判断语义搜索是否可用。
 * 启动时拉取一次，之后每 5 分钟轮询刷新。
 */
export const useVectorCapability = (
  refreshInterval = 5 * 60 * 1000
): UseVectorCapabilityResult => {
  const [status, setStatus] = useState<VectorEngineStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetch = useCallback(async () => {
    try {
      const resp = await systemService.getVectorStatus();
      if (resp.status === 'success' && resp.data) {
        setStatus(resp.data);
        setError(null);
      }
    } catch (err) {
      console.error('获取向量状态失败:', err);
      // 拉取失败时保守地认为不可用
      setStatus({
        enabled: false,
        driver: { available: false, path: '', error: '状态获取失败', version: '' },
        model: { available: false, path: '', error: '状态获取失败', dimension: 0 },
      });
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetch();
    const timer = setInterval(fetch, refreshInterval);
    return () => clearInterval(timer);
  }, [fetch, refreshInterval]);

  return {
    vectorEnabled: status?.enabled ?? false,
    status,
    loading,
    error,
    refresh: fetch,
  };
};
