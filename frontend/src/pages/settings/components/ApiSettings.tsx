import React from 'react';
import { Card, Form, Input, Alert, Row, Col } from 'antd';

const ApiSettings: React.FC = () => {
  return (
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
            rules={[{ required: true, message: '请输入API密钥' }]}
          >
            <Input.Password placeholder="输入OpenAI API密钥" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item 
            label="API基础URL" 
            name={['api', 'baseUrl']}
            rules={[{ required: true, message: '请输入API基础URL' }]}
          >
            <Input placeholder="例如: https://api.openai.com/v1" />
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

export default ApiSettings;
