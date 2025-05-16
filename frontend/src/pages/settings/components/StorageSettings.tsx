import React from 'react';
import { Card, Form, Input, InputNumber, Button, Typography, Row, Col } from 'antd';
import { ClearOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface StorageSettingsProps {
  clearCacheLoading: boolean;
  onClearCache: () => void;
}

const StorageSettings: React.FC<StorageSettingsProps> = ({ 
  clearCacheLoading, 
  onClearCache 
}) => {
  return (
    <Card title="存储设置" style={{ marginBottom: 16 }}>
      <Row gutter={24}>
        <Col span={12}>
          <Form.Item 
            label="存储根目录" 
            name={['storage', 'rootDirectory']}
            rules={[{ required: true, message: '请输入存储根目录' }]}
          >
            <Input placeholder="例如: ./data/images" />
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item 
            label="缓存目录" 
            name={['storage', 'cacheDirectory']}
            rules={[{ required: true, message: '请输入缓存目录' }]}
          >
            <Input placeholder="例如: ./data/caches" />
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
              onClick={onClearCache}
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
  );
};

export default StorageSettings;
