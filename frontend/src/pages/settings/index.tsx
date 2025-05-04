import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  Button,
  message,
  Divider,
  Typography,
  Space,
  Spin,
  Alert,
  Row,
  Col,
  Modal
} from 'antd';
import { SaveOutlined, ClearOutlined, ReloadOutlined, SettingOutlined, ExclamationCircleFilled } from '@ant-design/icons';
import { systemService } from '@/services/api';

const { Title, Text } = Typography;
const { Option } = Select;

// 系统配置接口
interface SystemSettings {
  storage: {
    rootDirectory: string;
    cacheDirectory: string;
    maxCacheSize: number;
  };
  api: {
    apiKey: string;
    baseUrl: string;
    timeout: number;
  };
  model: {
    vectorModel: string;
    visionModel: string;
  };
}

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [clearCacheLoading, setClearCacheLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [availableVisionModels, setAvailableVisionModels] = useState<string[]>([]);
  const [confirmModalVisible, setConfirmModalVisible] = useState(false);
  const [saveConfirmVisible, setSaveConfirmVisible] = useState(false);
  const [settingsToSave, setSettingsToSave] = useState<any>(null);
  
  // 加载系统配置和状态
  useEffect(() => {
    const fetchSystemInfo = async () => {
      try {
        setLoading(true);
        // 获取系统状态
        const statusResponse = await systemService.getSystemStatus();
        
        if (statusResponse.status === 'success' && statusResponse.data) {
          setSystemStatus(statusResponse.data);
          
          // 获取可用的视觉模型列表
          if (statusResponse.data.components?.multimodal_api?.available_models) {
            setAvailableVisionModels(statusResponse.data.components.multimodal_api.available_models);
          }
          
          // 获取系统配置
          const configResponse = await systemService.getSystemConfig();
          
          if (configResponse.status === 'success' && configResponse.data) {
            // 设置表单值
            form.setFieldsValue({
              storage: {
                rootDirectory: configResponse.data.storage.rootDirectory,
                cacheDirectory: configResponse.data.storage.cacheDirectory,
                maxCacheSize: configResponse.data.storage.maxCacheSize || 1.5
              },
              api: {
                apiKey: configResponse.data.api.apiKey,
                baseUrl: configResponse.data.api.baseUrl,
                timeout: configResponse.data.api.timeout
              },
              model: {
                visionModel: configResponse.data.model.visionModel
              }
            });
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
  }, [form]);

  // 保存设置
  const handleSaveSettings = async (values: any) => {
    // 保存要提交的值
    setSettingsToSave(values);
    // 显示确认对话框
    setSaveConfirmVisible(true);
  };

  // 确认保存设置
  const handleConfirmSave = async () => {
    try {
      setSaveLoading(true);
      
      // 调用API保存配置
      const response = await systemService.updateConfig(settingsToSave);
      
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
      const response = await systemService.clearCache(['all']);
      
      if (response.status === 'success') {
        message.success('缓存清除成功');
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

  // 渲染系统状态
  const renderSystemStatus = () => {
    if (!systemStatus) return null;
    
    // 获取数据库文件名
    const getFileName = (path: string) => {
      if (!path) return '';
      // 同时处理 / 和 \ 分隔符，适应不同操作系统
      const parts = path.split(/[\/\\]/);
      return parts[parts.length - 1];
    };
    
    return (
      <Card title="系统状态" style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Card size="small" title="系统">
              <p><strong>版本:</strong> {systemStatus.system.version}</p>
              <p><strong>状态:</strong> {systemStatus.system.status}</p>
              <p><strong>平台:</strong> {systemStatus.system.platform}</p>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small" title="数据库">
              <p><strong>状态:</strong> {systemStatus.components.database.status}</p>
              <p><strong>类型:</strong> {systemStatus.components.database.type}</p>
              <p><strong>路径:</strong> {getFileName(systemStatus.components.database.path)}</p>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small" title="存储">
              <p><strong>图片总数:</strong> {systemStatus.storage?.total_images || 0}</p>
              <p><strong>标签总数:</strong> {systemStatus.storage?.total_tags || 0}</p>
              <p><strong>存储大小:</strong> {systemStatus.storage?.total_size_mb || 0} MB</p>
            </Card>
          </Col>
        </Row>
      </Card>
    );
  };

  return (
    <div className="settings-page">
      <Title level={4}>
        <SettingOutlined /> 系统设置
      </Title>
      <Text type="secondary">
        配置 SmartImageFinder 的各项参数，修改后点击"保存设置"按钮生效
      </Text>

      <Divider />

      <Spin spinning={loading}>
        {renderSystemStatus()}

        <Form
          form={form}
          layout="vertical"
          onFinish={handleSaveSettings}
        >
          <Card title="存储设置" style={{ marginBottom: 16 }}>
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item 
                  label="存储根目录" 
                  name={['storage', 'rootDirectory']}
                  rules={[{ required: true, message: '请输入存储根目录' }]}
                >
                  <Input placeholder="例如: C:/SmartImageFinder/data" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item 
                  label="缓存目录" 
                  name={['storage', 'cacheDirectory']}
                  rules={[{ required: true, message: '请输入缓存目录' }]}
                >
                  <Input placeholder="例如: C:/SmartImageFinder/cache" />
                </Form.Item>
              </Col>
            </Row>
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item 
                  label="最大缓存大小 (GB)" 
                  name={['storage', 'maxCacheSize']}
                  rules={[{ required: true, message: '请输入最大缓存大小' }]}
                  tooltip="设置系统缓存的最大占用空间，默认为1.5GB"
                >
                  <InputNumber min={0.5} max={10} step={0.5} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col span={12}>
                <div style={{ marginTop: 29 }}>
                  <Button 
                    type="primary" 
                    danger 
                    icon={<ClearOutlined />} 
                    onClick={showClearCacheConfirm}
                    loading={clearCacheLoading}
                  >
                    清除缓存
                  </Button>
                  <Text type="secondary" style={{ marginLeft: 8 }}>
                    清除系统缓存，包括向量缓存
                  </Text>
                </div>
              </Col>
            </Row>
          </Card>

          <Card title="API设置" style={{ marginBottom: 16 }}>
            <Alert
              message="API密钥是敏感信息，请妥善保管"
              type="warning"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Row gutter={24}>
              <Col span={12}>
                <Form.Item 
                  label="API密钥" 
                  name={['api', 'apiKey']}
                >
                  <Input.Password placeholder="输入OpenAI API密钥" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item 
                  label="API基础URL" 
                  name={['api', 'baseUrl']}
                >
                  <Input placeholder="例如: http://localhost:8000" />
                </Form.Item>
              </Col>
            </Row>
            <Row>
              <Col span={12}>
                <Form.Item 
                  label="超时时间 (毫秒)" 
                  name={['api', 'timeout']}
                >
                  <InputNumber min={1000} max={60000} step={1000} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>
          </Card>

          <Card title="模型设置" style={{ marginBottom: 16 }}>
            <Row>
              <Col span={24}>
                <Form.Item 
                  label="视觉模型" 
                  name={['model', 'visionModel']}
                >
                  <Select>
                    {availableVisionModels.map(model => (
                      <Option key={model} value={model}>{model}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Card>

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