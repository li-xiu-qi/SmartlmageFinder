import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  InputNumber,
  Select,
  Button,
  Switch,
  message,
  Tabs,
  Divider,
  Typography,
  Space,
  Spin,
  Alert,
  Row,
  Col
} from 'antd';
import { SaveOutlined, ClearOutlined, ReloadOutlined, SettingOutlined } from '@ant-design/icons';
import { systemService } from '@/services/api';

const { Title, Text } = Typography;
const { TabPane } = Tabs;
const { Option } = Select;

// 模拟的系统配置
interface SystemSettings {
  general: {
    pageSize: number;
    theme: string;
    language: string;
  };
  storage: {
    rootDirectory: string;
    cacheDirectory: string;
    maxFileSize: number;
  };
  api: {
    apiKey: string;
    baseUrl: string;
    timeout: number;
  };
  model: {
    vectorModel: string;
    visionModel: string;
    batchSize: number;
    enableCache: boolean;
  };
}

const SettingsPage: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [clearCacheLoading, setClearCacheLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<any>(null);
  
  // 模拟的初始配置
  const defaultSettings: SystemSettings = {
    general: {
      pageSize: 20,
      theme: 'light',
      language: 'zh-CN',
    },
    storage: {
      rootDirectory: 'C:/SmartImageFinder/data',
      cacheDirectory: 'C:/SmartImageFinder/cache',
      maxFileSize: 50,
    },
    api: {
      apiKey: '', // 敏感信息，不显示
      baseUrl: 'http://localhost:8000',
      timeout: 30000,
    },
    model: {
      vectorModel: 'jina-clip-v2',
      visionModel: 'Qwen2.5-VL-32B-Instruct',
      batchSize: 16,
      enableCache: true,
    },
  };

  // 加载系统配置和状态
  useEffect(() => {
    const fetchSystemInfo = async () => {
      try {
        setLoading(true);
        // 获取系统状态，在真实项目中会从后端获取
        const response = await systemService.getSystemStatus();
        
        if (response.status === 'success' && response.data) {
          setSystemStatus(response.data);
          
          // 在真实项目中，这里会加载配置数据
          // 这里使用模拟数据填充表单
          form.setFieldsValue({
            general: defaultSettings.general,
            storage: defaultSettings.storage,
            api: defaultSettings.api,
            model: defaultSettings.model,
          });
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
    try {
      setSaveLoading(true);
      // 模拟保存配置到后端
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      message.success('设置保存成功');
      console.log('保存的设置:', values);
    } catch (error) {
      console.error('保存设置失败:', error);
      message.error('保存设置失败');
    } finally {
      setSaveLoading(false);
    }
  };

  // 清除缓存
  const handleClearCache = async () => {
    try {
      setClearCacheLoading(true);
      const response = await systemService.clearCache(['all']);
      
      if (response.status === 'success') {
        message.success('缓存清除成功');
      }
    } catch (error) {
      console.error('清除缓存失败:', error);
      message.error('清除缓存失败');
    } finally {
      setClearCacheLoading(false);
    }
  };

  // 渲染系统状态
  const renderSystemStatus = () => {
    if (!systemStatus) return null;
    
    return (
      <Card title="系统状态" style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Card size="small" title="系统">
              <p><strong>版本:</strong> {systemStatus.system.version}</p>
              <p><strong>状态:</strong> {systemStatus.system.status}</p>
              <p><strong>运行时间:</strong> {Math.floor(systemStatus.system.uptime / 3600)} 小时</p>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small" title="组件">
              <p><strong>模型:</strong> {systemStatus.components.model.name}</p>
              <p><strong>数据库:</strong> {systemStatus.components.database.type} {systemStatus.components.database.version}</p>
              <p><strong>多模态API:</strong> {systemStatus.components.multimodal_api.model}</p>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card size="small" title="存储">
              <p><strong>图片总数:</strong> {systemStatus.storage.total_images}</p>
              <p><strong>存储大小:</strong> {systemStatus.storage.total_size_mb} MB</p>
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
          <Tabs defaultActiveKey="general">
            <TabPane tab="常规设置" key="general">
              <Card>
                <Form.Item 
                  label="每页图片数量" 
                  name={['general', 'pageSize']}
                  rules={[{ required: true, message: '请输入每页图片数量' }]}
                >
                  <InputNumber min={10} max={100} />
                </Form.Item>

                <Form.Item 
                  label="主题" 
                  name={['general', 'theme']}
                >
                  <Select>
                    <Option value="light">浅色</Option>
                    <Option value="dark">深色</Option>
                    <Option value="system">跟随系统</Option>
                  </Select>
                </Form.Item>

                <Form.Item 
                  label="语言" 
                  name={['general', 'language']}
                >
                  <Select>
                    <Option value="zh-CN">中文（简体）</Option>
                    <Option value="en-US">English (US)</Option>
                  </Select>
                </Form.Item>
              </Card>
            </TabPane>

            <TabPane tab="存储设置" key="storage">
              <Card>
                <Form.Item 
                  label="存储根目录" 
                  name={['storage', 'rootDirectory']}
                  rules={[{ required: true, message: '请输入存储根目录' }]}
                >
                  <Input placeholder="例如: C:/SmartImageFinder/data" />
                </Form.Item>

                <Form.Item 
                  label="缓存目录" 
                  name={['storage', 'cacheDirectory']}
                  rules={[{ required: true, message: '请输入缓存目录' }]}
                >
                  <Input placeholder="例如: C:/SmartImageFinder/cache" />
                </Form.Item>

                <Form.Item 
                  label="最大文件大小 (MB)" 
                  name={['storage', 'maxFileSize']}
                  rules={[{ required: true, message: '请输入最大文件大小' }]}
                >
                  <InputNumber min={1} max={1000} />
                </Form.Item>

                <div style={{ marginTop: 16 }}>
                  <Button 
                    type="primary" 
                    danger 
                    icon={<ClearOutlined />} 
                    onClick={handleClearCache}
                    loading={clearCacheLoading}
                  >
                    清除缓存
                  </Button>
                  <Text type="secondary" style={{ marginLeft: 8 }}>
                    清除系统缓存，包括向量缓存和图片分析缓存
                  </Text>
                </div>
              </Card>
            </TabPane>

            <TabPane tab="API设置" key="api">
              <Card>
                <Alert
                  message="API密钥是敏感信息，请妥善保管"
                  type="warning"
                  showIcon
                  style={{ marginBottom: 16 }}
                />

                <Form.Item 
                  label="API密钥" 
                  name={['api', 'apiKey']}
                >
                  <Input.Password placeholder="输入OpenAI API密钥" />
                </Form.Item>

                <Form.Item 
                  label="API基础URL" 
                  name={['api', 'baseUrl']}
                >
                  <Input placeholder="例如: http://localhost:8000" />
                </Form.Item>

                <Form.Item 
                  label="超时时间 (毫秒)" 
                  name={['api', 'timeout']}
                >
                  <InputNumber min={1000} max={60000} step={1000} />
                </Form.Item>
              </Card>
            </TabPane>

            <TabPane tab="模型设置" key="model">
              <Card>
                <Form.Item 
                  label="向量模型" 
                  name={['model', 'vectorModel']}
                >
                  <Select>
                    <Option value="jina-clip-v2">jina-clip-v2</Option>
                    <Option value="openai-clip">openai-clip</Option>
                    <Option value="clip-vit-b32">clip-vit-b32</Option>
                  </Select>
                </Form.Item>

                <Form.Item 
                  label="视觉模型" 
                  name={['model', 'visionModel']}
                >
                  <Select>
                    <Option value="Qwen2.5-VL-32B-Instruct">Qwen2.5-VL-32B-Instruct</Option>
                    <Option value="gpt-4-vision-preview">gpt-4-vision-preview</Option>
                    <Option value="gemini-pro-vision">gemini-pro-vision</Option>
                  </Select>
                </Form.Item>

                <Form.Item 
                  label="批处理大小" 
                  name={['model', 'batchSize']}
                >
                  <InputNumber min={1} max={64} />
                </Form.Item>

                <Form.Item 
                  label="启用模型缓存" 
                  name={['model', 'enableCache']} 
                  valuePropName="checked"
                >
                  <Switch />
                </Form.Item>
              </Card>
            </TabPane>
          </Tabs>

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
    </div>
  );
};

export default SettingsPage;