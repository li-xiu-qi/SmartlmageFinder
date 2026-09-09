import React, { useState, useEffect, useCallback } from 'react';
import {
  Form,
  Button,
  message,
  Spin,
  Card,
} from 'antd';
import {
  SaveOutlined,
  ReloadOutlined,
  ExclamationCircleFilled,
} from '@ant-design/icons';
import { Activity, SlidersHorizontal, RefreshCw } from 'lucide-react';
import systemService from '@/services/systemService';
import { SystemStatusData, SystemConfig } from '@/types/system';
import {
  SystemStatus,
  StorageSettings,
  ApiSettings,
  ModelSettings,
  VectorDbSettings,
  SystemRuntime
} from './components';
import RefModal from '@/components/RefModal';
import { cn } from '@/lib/utils';

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [clearCacheLoading, setClearCacheLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatusData | null>(null);
  const [confirmModalVisible, setConfirmModalVisible] = useState(false);
  const [saveConfirmVisible, setSaveConfirmVisible] = useState(false);
  const [settingsToSave, setSettingsToSave] = useState<SystemConfig | null>(null);
  const [activeTab, setActiveTab] = useState('status');

  // 使用useCallback包装fetchSystemInfo函数以便可以在useEffect依赖数组中使用
  const fetchSystemInfo = useCallback(async () => {
    try {
      setLoading(true);

      // 1. 获取系统配置信息
      const configResponse = await systemService.getSystemConfig();
      if (configResponse.status !== 'success') {
        message.error('获取系统配置失败');
        return;
      }

      // 2. 获取各种系统状态信息
      const [infoResponse, databaseResponse, storageResponse, cacheResponse, vectorDriverResponse] = 
        await Promise.all([
          systemService.getSystemInfo(),
          systemService.getDatabaseInfo(),
          systemService.getStorageInfo(),
          systemService.getCacheInfo(),
          systemService.getVectorDbDriverStatus()
        ]);

      // 3. 检查所有请求是否成功
      if (infoResponse.status !== 'success' || 
          databaseResponse.status !== 'success' || 
          storageResponse.status !== 'success' || 
          cacheResponse.status !== 'success' ||
          vectorDriverResponse.status !== 'success') {
        message.error('获取系统状态信息失败');
        return;
      }

      // 4. 从配置中获取多模态API信息
      const apiStatus = configResponse.data.api.apiKey ? 'enabled' as const : 'disabled' as const;
      
      // 确保我们能获取到视觉模型设置
      console.log('配置中的视觉模型:', configResponse.data.model.visionModel);
      console.log('配置中的可用模型:', configResponse.data.model.availableModels);
      
      const multimodalApi = {
        status: apiStatus,
        model: configResponse.data.model.visionModel || 'default',
        available_models: configResponse.data.model.availableModels || [],
        api_base: configResponse.data.api.baseUrl || ''
      };

      // 5. 组装系统状态对象
      const combinedStatus: SystemStatusData = {
        system: infoResponse.data,
        components: {
          database: databaseResponse.data,
          vector_db_driver: vectorDriverResponse.data,
          multimodal_api: multimodalApi
        },
        storage: storageResponse.data,
        cache: cacheResponse.data,
        models: {
          embedding_model: infoResponse.data.models_info?.embedding_model || '未知',
          embedding_dimension: infoResponse.data.models_info?.embedding_dimension
        },
        server: {
          host: 'localhost',
          port: 8000
        }
      };
      
      setSystemStatus(combinedStatus);
      
      // 6. 设置表单初始值
      form.setFieldsValue(configResponse.data);
      
    } catch (error) {
      console.error('获取系统信息失败:', error);
      message.error('获取系统信息失败');
    } finally {
      setLoading(false);
    }
  }, [form]);

  // 加载系统配置和状态
  useEffect(() => {
    fetchSystemInfo();
  }, [fetchSystemInfo]);

  // 保存设置
  const handleSaveSettings = async (values: SystemConfig) => {
    // 打印表单值，验证视觉模型是否正确保存
    if (import.meta.env.DEV) {
      console.log('保存的表单值:', values);
      console.log('保存的视觉模型:', values.model?.visionModel);
      console.log('保存的可用视觉模型列表:', values.model?.availableModels);
    }
    
    // 保存要提交的值
    setSettingsToSave(values);
    // 显示确认对话框
    setSaveConfirmVisible(true);
  };

  // 确认保存设置
  const handleConfirmSave = async () => {
    if (!settingsToSave) return;

    try {
      setSaveLoading(true);

      // 调用API保存配置
      const response = await systemService.updateSystemConfig(settingsToSave);

      if (response.status === 'success') {
        message.success('设置保存成功');
        // 重新获取系统信息以更新状态
        fetchSystemInfo();
      } else {
        message.error(response.error?.message || '保存设置失败');
      }    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : '未知错误';
      console.error('保存设置失败:', errorMessage);
      message.error(`保存设置失败: ${errorMessage}`);
    }finally {
      setSaveLoading(false);
      setSaveConfirmVisible(false);
    }
  };

  // 取消保存设置
  const handleCancelSave = () => {
    setSaveConfirmVisible(false);
  };

  // 显示清除缓存确认对话框
  const showClearCacheConfirm = () => {
    setConfirmModalVisible(true);
  };

  // 确认清除缓存
  const handleConfirmClearCache = async () => {
    try {
      setClearCacheLoading(true);
  const beforeLastScan = systemStatus?.cache.last_scan;
  const response = await systemService.clearCache();

      if (response.status === 'success') {
        message.success(`缓存清除成功，释放了 ${response.data?.total_size_freed_mb.toFixed(2)} MB 空间`);

        // 快速轮询缓存精简信息，等待 last_scan 变化（最多 5 次，每 600ms）
        let attempts = 0;
        let updated = false;
        while (attempts < 5) {
          attempts += 1;
          try {
            const brief = await systemService.getCacheBrief();
            if (brief.status === 'success') {
              if (!beforeLastScan || (brief.data.last_scan && brief.data.last_scan !== beforeLastScan)) {
                // 局部更新 systemStatus.cache 以减少一次完整刷新耗时
                setSystemStatus(prev => prev ? {
                  ...prev,
                  cache: {
                    ...prev.cache,
                    total_size_mb: brief.data.total_size_mb,
                    last_scan: brief.data.last_scan ?? prev.cache.last_scan
                  }
                } : prev);
                updated = true;
                break;
              }
            }
          } catch {
            // 忽略单次失败
          }
          await new Promise(r => setTimeout(r, 600));
        }
        // 若轮询未成功更新，再做一次完整刷新
        if (!updated) {
          fetchSystemInfo();
        }
      } else {
        message.error(response.error?.message || '清除缓存失败');
      }
    } catch (error) {
      console.error('清除缓存失败:', error);
      message.error('清除缓存失败');
    } finally {
      setClearCacheLoading(false);
      setConfirmModalVisible(false);
    }
  };

  // 取消清除缓存
  const handleCancelClearCache = () => {
    setConfirmModalVisible(false);
  };
    // 刷新系统状态
  const refreshSystemStatus = async () => {
    try {
      // 直接调用已有的系统信息获取方法
      fetchSystemInfo();
      message.success('系统状态已更新');
    } catch (error) {
      console.error('获取系统状态失败:', error);
      message.error('获取系统状态失败');
    }
  };

  const navItems = [
    { key: 'status', label: '系统状态', icon: Activity },
    { key: 'settings', label: '系统配置', icon: SlidersHorizontal },
  ];

  return (
    <div className="space-y-6">
      {/* 标题区 */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <h1 className="font-serif text-2xl font-semibold tracking-tight text-foreground">系统设置</h1>
          <p className="text-sm text-muted-foreground">
            查看运行状态，或调整存储、API、模型与向量库参数。部分配置需重启后生效。
          </p>
        </div>
        <button
          type="button"
          onClick={refreshSystemStatus}
          className="inline-flex h-9 items-center gap-2 rounded-md border border-input bg-card px-4 text-sm font-medium text-secondary-foreground shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground"
        >
          <RefreshCw className="h-4 w-4" strokeWidth={1.9} />
          刷新状态
        </button>
      </div>

      <Spin spinning={loading}>
        <div className="flex flex-col gap-6 md:flex-row">
          {/* 左侧分段导航 */}
          <nav className="flex shrink-0 gap-1 overflow-x-auto md:w-44 md:flex-col">
            {navItems.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                type="button"
                onClick={() => setActiveTab(key)}
                className={cn(
                  'flex h-10 shrink-0 items-center gap-2.5 rounded-md px-3.5 text-sm font-medium transition-colors',
                  activeTab === key
                    ? 'bg-accent text-accent-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                <Icon className="h-[18px] w-[18px]" strokeWidth={1.8} />
                {label}
              </button>
            ))}
          </nav>

          {/* 内容面板 */}
          <div className="min-w-0 flex-1">
            {activeTab === 'status' && (
              <div className="space-y-4">
                <SystemRuntime />
                {systemStatus && <SystemStatus systemStatus={systemStatus} />}
              </div>
            )}

            {activeTab === 'settings' && (
              <Form form={form} layout="vertical" onFinish={handleSaveSettings}>
                <StorageSettings
                  clearCacheLoading={clearCacheLoading}
                  onClearCache={showClearCacheConfirm}
                  systemStatus={systemStatus}
                  loading={loading}
                />
                <ApiSettings loading={loading} />
                <ModelSettings systemStatus={systemStatus} loading={loading} form={form} />
                <VectorDbSettings systemStatus={systemStatus} loading={loading} />

                <Card>
                  <div className="flex flex-wrap gap-3">
                    <Button
                      type="primary"
                      htmlType="submit"
                      icon={<SaveOutlined />}
                      loading={saveLoading}
                      size="large"
                    >
                      保存设置
                    </Button>
                    <Button icon={<ReloadOutlined />} onClick={() => form.resetFields()} size="large">
                      重置
                    </Button>
                  </div>
                </Card>
              </Form>
            )}
          </div>
        </div>
      </Spin>

      {/* 清除缓存确认对话框 */}      <RefModal
        title={
          <span>
            <ExclamationCircleFilled style={{ color: '#d97706', marginRight: 8 }} />
            确认清除缓存
          </span>
        }
        open={confirmModalVisible}
        onOk={handleConfirmClearCache}
        onCancel={handleCancelClearCache}
        confirmLoading={clearCacheLoading}
        okText="确认清除"
        cancelText="取消"
        okButtonProps={{ danger: true }}
      >
        <p>清除缓存将删除所有向量缓存数据，可能会导致下次搜索速度变慢。确定要继续吗？</p>
        <p className="text-sm text-muted-foreground">
          当前缓存大小: {systemStatus?.cache.total_size_mb.toFixed(2) || "0.00"} MB
        </p>
      </RefModal>

      {/* 保存设置确认对话框 */}
      <RefModal
        title={
          <span>
            <ExclamationCircleFilled style={{ color: '#d97706', marginRight: 8 }} />
            确认保存设置
          </span>
        }
        open={saveConfirmVisible}
        onOk={handleConfirmSave}
        onCancel={handleCancelSave}
        confirmLoading={saveLoading}
        okText="确认保存"
        cancelText="取消"
      >
        <p>保存的设置将直接写入配置文件，应用需要重启后部分设置才能生效。确定要保存吗？</p>
        <div className="text-sm text-muted-foreground">
          <ul className="list-disc pl-5">
            <li>API设置: 立即生效</li>
            <li>存储设置: 需重启后生效</li>
            <li>模型设置: 立即生效</li>
            <li>向量数据库设置: 需重启后生效</li>
          </ul>
        </div>
      </RefModal>
    </div>
  );
};

export default SettingsPage;
