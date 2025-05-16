import { useState, useEffect } from 'react';
import { systemService } from '@/services/api';

export type SystemStatus = 'healthy' | 'warning' | 'error' | undefined;

interface UseSystemStatusResult {
  systemStatus: SystemStatus;
  loading: boolean;
  error: Error | null;
  refreshStatus: () => Promise<void>;
}

/**
 * 系统状态自定义钩子
 * @param refreshInterval 刷新间隔时间(毫秒)，默认为 5 分钟
 */
export const useSystemStatus = (refreshInterval = 5 * 60 * 1000): UseSystemStatusResult => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus>(undefined);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchSystemStatus = async () => {
    setLoading(true);
    try {
      const response = await systemService.getSystemStatus();
      if (response.status === 'success' && response.data) {
        setSystemStatus(response.data.system.status);
        setError(null);
      } else {
        throw new Error('系统状态获取失败');
      }
    } catch (err) {
      console.error('获取系统状态失败:', err);
      setSystemStatus('error');
      setError(err instanceof Error ? err : new Error(String(err)));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemStatus();
    
    // 设置定时刷新
    const interval = setInterval(fetchSystemStatus, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  return { systemStatus, loading, error, refreshStatus: fetchSystemStatus };
};
