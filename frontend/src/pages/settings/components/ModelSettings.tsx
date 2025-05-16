import React from 'react';
import { Card, Form, Input, Select, Row, Col } from 'antd';
import { SystemStatusData } from '@/types/system';

const { Option } = Select;

interface ModelSettingsProps {
  systemStatus: SystemStatusData | null;
}

const ModelSettings: React.FC<ModelSettingsProps> = ({ systemStatus }) => {
  return (
    <Card title="模型设置" style={{ marginBottom: 16 }}>
      <Row gutter={24}>
        <Col span={12}>
          <Form.Item 
            label="向量模型" 
            name={['model', 'vectorModel']}
            rules={[{ required: true, message: '请选择向量模型' }]}
          >
            <Input placeholder="例如: text-embedding-3-small" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item 
            label="视觉模型" 
            name={['model', 'visionModel']}
            rules={[{ required: true, message: '请选择视觉模型' }]}
          >
            <Select placeholder="选择视觉模型">
              {systemStatus?.components.multimodal_api.available_models.map((model: string) => (
                <Option key={model} value={model}>{model}</Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

export default ModelSettings;
