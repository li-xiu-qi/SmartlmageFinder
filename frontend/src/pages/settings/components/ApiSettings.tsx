import React from 'react';
import { Card, Form, Input, Alert, Row, Col, Tooltip } from 'antd';
import { EyeInvisibleOutlined, EyeTwoTone, InfoCircleOutlined } from '@ant-design/icons';

interface ApiSettingsProps {
  loading?: boolean;
}

const ApiSettings: React.FC<ApiSettingsProps> = ({ loading = false }) => {

  return (
    <Card 
      title={
        <span>
          API设置 
          <Tooltip title="配置连接到OpenAI或其他兼容服务的API参数">
            <InfoCircleOutlined style={{ marginLeft: 8, color: '#1890ff' }} />
          </Tooltip>
        </span>
      } 
      style={{ marginBottom: 16 }}
    >
      <Alert
        message="API密钥是敏感信息，请妥善保管"
        description="密钥将仅保存在服务器端配置文件中，不会被传输到任何第三方服务"
        type="warning"
        showIcon
        style={{ marginBottom: 16 }}
      />
      <Row gutter={24}>
        <Col span={12}>
          <Form.Item 
            label="API密钥" 
            name={['api', 'apiKey']}
            rules={[{ required: true, message: '请输入API密钥' }]}
            tooltip="OpenAI API密钥，用于访问GPT模型和Embedding功能"
          >
            <Input.Password 
              placeholder="输入OpenAI API密钥" 
              disabled={loading}
              iconRender={(visible) => (visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />)}
            />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item 
            label="API基础URL" 
            name={['api', 'baseUrl']}
            rules={[
              { required: true, message: '请输入API基础URL' },
              { type: 'url', message: '请输入有效的URL' }
            ]}
            tooltip="API服务器地址，可使用OpenAI官方API或兼容服务"
          >
            <Input 
              placeholder="例如: https://api.openai.com/v1" 
              disabled={loading}
              suffix={
                <Tooltip title="留空则使用OpenAI默认地址">
                  <InfoCircleOutlined style={{ color: 'rgba(0,0,0,.45)' }} />
                </Tooltip>
              }
            />
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

export default ApiSettings;
