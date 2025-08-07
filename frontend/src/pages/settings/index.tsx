import React, { useState, useEffect, useCallback } from 'react';
import {
  Form,
  Button,
  message,
  Typography,
  Space,
  Spin,
  Row,
  Col,
  Card,
  Tabs
} from 'antd';
import {
  SaveOutlined,
  ReloadOutlined,
  SettingOutlined,
  ExclamationCircleFilled,
  SyncOutlined,
  HddOutlined
} from '@ant-design/icons';
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


const { Title, Paragraph } = Typography;

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

      const response = await systemService.clearCache();

      if (response.status === 'success') {
        message.success(`缓存清除成功，释放了 ${response.data?.total_size_freed_mb.toFixed(2)} MB 空间`);

        // 重新获取系统状态以更新缓存信息
        fetchSystemInfo();
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

  return (
    <div className="settings-page">
      <Row gutter={[0, 16]}>
        <Col span={24}>
          <Card>
            <Title level={4}>
              <SettingOutlined /> 系统设置
            </Title>
            <Paragraph type="secondary">
              配置 SmartImageFinder 的各项参数，修改后点击"保存设置"按钮生效。部分设置项可能需要重启系统才能生效。
            </Paragraph>
          </Card>
        </Col>
      </Row>

      <Spin spinning={loading}>
        <Row gutter={[0, 16]}>
          <Col span={24}>
            <Tabs
              defaultActiveKey="status"
              activeKey={activeTab}
              onChange={setActiveTab}
              tabPosition="top"
              type="card"
              tabBarExtraContent={
                <Button
                  type="primary"
                  icon={<SyncOutlined />}
                  onClick={refreshSystemStatus}
                >
                  刷新状态
                </Button>
              }
              items={[
                {
                  key: 'status',
                  label: <span><HddOutlined /> 系统状态</span>,
                  children: (
                    <>
                      <SystemRuntime />
                      {systemStatus && <SystemStatus systemStatus={systemStatus} />}
                    </>
                  )
                },
                {
                  key: 'settings',
                  label: <span><SettingOutlined /> 系统配置</span>,
                  children: activeTab === 'settings' ? (
                    <Form
                      form={form}
                      layout="vertical"
                      onFinish={handleSaveSettings}
                    >
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
                        <div className="settings-actions">
                          <Space size="large">
                            <Button
                              type="primary"
                              htmlType="submit"
                              icon={<SaveOutlined />}
                              loading={saveLoading}
                              size="large"
                            >
                              保存设置
                            </Button>
                            <Button
                              icon={<ReloadOutlined />}
                              onClick={() => form.resetFields()}
                              size="large"
                            >
                              重置
                            </Button>
                          </Space>
                        </div>
                      </Card>
                    </Form>
                  ) : null
                }
              ]}
            />
          </Col>
        </Row>      </Spin>

      {/* 清除缓存确认对话框 */}      <RefModal
        title={
          <span>
            <ExclamationCircleFilled style={{ color: '#faad14', marginRight: 8 }} />
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
        <Paragraph type="secondary">
          当前缓存: {systemStatus?.cache.total_entries || 0} 条, {systemStatus?.cache.total_size_mb.toFixed(2) || "0.00"} MB        </Paragraph>
      </RefModal>

      {/* 保存设置确认对话框 */}
      <RefModal
        title={
          <span>
            <ExclamationCircleFilled style={{ color: '#faad14', marginRight: 8 }} />
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
        <Paragraph type="secondary">
          <ul>
            <li>API设置: 立即生效</li>
            <li>存储设置: 需重启后生效</li>
            <li>模型设置: 立即生效</li>
            <li>向量数据库设置: 需重启后生效</li>          </ul>
        </Paragraph>
      </RefModal>
    </div>
  );
};

export default SettingsPage;
