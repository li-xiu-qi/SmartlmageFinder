import React, { useState, useEffect } from 'react';
import {
  Form,
  Button,
  message,
  Divider,
  Typography,
  Space,
  Spin,
  Modal
} from 'antd';
import { SaveOutlined, ReloadOutlined, SettingOutlined, ExclamationCircleFilled } from '@ant-design/icons';
import systemService from '@/services/systemService';
import { SystemStatusData, SystemConfig } from '@/types/system';
import { 
  SystemStatus, 
  StorageSettings, 
  ApiSettings, 
  ModelSettings, 
  VectorDbSettings 
} from './components';

const { Title, Text } = Typography;

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [clearCacheLoading, setClearCacheLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatusData | null>(null);
  const [confirmModalVisible, setConfirmModalVisible] = useState(false);
  const [saveConfirmVisible, setSaveConfirmVisible] = useState(false);
  const [settingsToSave, setSettingsToSave] = useState<SystemConfig | null>(null);
  
  // 加载系统配置和状态
  useEffect(() => {
    const fetchSystemInfo = async () => {
      try {
        setLoading(true);
        // 获取系统状态
        const statusResponse = await systemService.getSystemStatus();
        
        if (statusResponse.status === 'success' && statusResponse.data) {
          setSystemStatus(statusResponse.data);
          
          // 获取系统配置
          const configResponse = await systemService.getSystemConfig();
          
          if (configResponse.status === 'success' && configResponse.data) {
            // 设置表单值
            form.setFieldsValue(configResponse.data);
          }
        }
      } catch (error) {
        console.error('获取系统信息失败:', error);
        message.error('获取系统信息失败');
      } finally {
        setLoading(false);
      }
    };

    fetchSystemInfo();
  }, [form]);  // 保存设置
  const handleSaveSettings = async (values: SystemConfig) => {
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
      } else {
        message.error(response.error?.message || '保存设置失败');
      }
    } catch (error: any) {
      console.error('保存设置失败:', error);
      message.error(`保存设置失败: ${error.message || '未知错误'}`);
    } finally {
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
        message.success('缓存清除成功');
        
        // 刷新缓存统计
        const statsResponse = await systemService.getCacheStats();
        if (statsResponse.status === 'success' && statsResponse.data) {
          // 更新界面上的缓存信息
          // 可以根据需要更新systemStatus，但需要深拷贝避免直接修改状态
          if (systemStatus) {
            const updatedStatus = { ...systemStatus } as SystemStatusData;
            updatedStatus.cache.text_vector_cache.entries = statsResponse.data.text_vector_cache.entries;
            updatedStatus.cache.text_vector_cache.size_mb = statsResponse.data.text_vector_cache.size_mb;
            updatedStatus.cache.image_vector_cache.entries = statsResponse.data.image_vector_cache.entries;
            updatedStatus.cache.image_vector_cache.size_mb = statsResponse.data.image_vector_cache.size_mb;
            setSystemStatus(updatedStatus);
          }
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
  };  return (
    <div className="settings-page">
      <Title level={4}>
        <SettingOutlined /> 系统设置
      </Title>
      <Text type="secondary">
        配置 SmartImageFinder 的各项参数，修改后点击"保存设置"按钮生效
      </Text>

      <Divider />

      <Spin spinning={loading}>
        {systemStatus && <SystemStatus systemStatus={systemStatus} />}
        
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSaveSettings}
        >
          <StorageSettings 
            clearCacheLoading={clearCacheLoading} 
            onClearCache={showClearCacheConfirm}
          />
          
          <ApiSettings />
          
          <ModelSettings systemStatus={systemStatus} />
          
          <VectorDbSettings />

          <div style={{ marginTop: 16, textAlign: 'center' }}>
            <Space>
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
        </Form>
      </Spin>

      {/* 清除缓存确认对话框 */}
      <Modal
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
      </Modal>

      {/* 保存设置确认对话框 */}
      <Modal
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
      </Modal>
    </div>
  );
};

export default SettingsPage;