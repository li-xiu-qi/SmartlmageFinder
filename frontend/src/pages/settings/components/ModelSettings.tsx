import React from 'react';
import { Card, Form, Select, Row, Col, Tooltip, Skeleton } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { SystemStatusData } from '@/types/system';

const { Option } = Select;

interface ModelSettingsProps {
  systemStatus: SystemStatusData | null;
  loading?: boolean;
}

const ModelSettings: React.FC<ModelSettingsProps> = ({ systemStatus, loading = false }) => {
  // 从系统状态获取可用的模型列表，如果没有则提供默认选项
  const availableModels = systemStatus?.components.multimodal_api.available_models || [];
  const hasAvailableModels = availableModels.length > 0;

  return (
    <Card 
      title={
        <span>
          模型设置 
          <Tooltip title="配置用于图像分析和向量嵌入的AI模型">
            <InfoCircleOutlined style={{ marginLeft: 8, color: '#1890ff' }} />
          </Tooltip>
        </span>
      } 
      style={{ marginBottom: 16 }}
    >
      {loading ? (
        <Skeleton active paragraph={{ rows: 3 }} />
      ) : (
        <Row gutter={24}>
          <Col span={12}>
            <Form.Item 
              label="向量模型" 
              name={['model', 'vectorModel']}
              rules={[{ required: true, message: '请选择向量模型' }]}
              tooltip="用于生成文本和图像嵌入的模型，影响搜索的精度和性能"
            >
              <Select placeholder="选择向量模型">
                <Option value="text-embedding-3-small">text-embedding-3-small</Option>
                <Option value="text-embedding-3-large">text-embedding-3-large</Option>
                <Option value="text-embedding-ada-002">text-embedding-ada-002 (旧版)</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item 
              label="视觉模型" 
              name={['model', 'visionModel']}
              rules={[{ required: true, message: '请选择视觉模型' }]}
              tooltip="用于图像识别和多模态处理的模型，影响图像分析的准确度"
            >
              <Select 
                placeholder="选择视觉模型"
                disabled={loading}
                loading={loading}
              >
                {hasAvailableModels ? (
                  availableModels.map((model: string) => (
                    <Option key={model} value={model}>{model}</Option>
                  ))
                ) : (
                  <>
                    <Option value="gpt-4-vision-preview">gpt-4-vision-preview</Option>
                    <Option value="gpt-4o">gpt-4o</Option>
                  </>
                )}
              </Select>
            </Form.Item>
          </Col>
        </Row>
      )}
    </Card>
  );
};

export default ModelSettings;
