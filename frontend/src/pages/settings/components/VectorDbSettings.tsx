import React from 'react';
import { Card, Form, Input, Row, Col } from 'antd';

const VectorDbSettings: React.FC = () => {
  return (
    <Card title="向量数据库设置" style={{ marginBottom: 16 }}>
      <Row>
        <Col span={24}>
          <Form.Item 
            label="驱动路径" 
            name={['vectorDb', 'driverPath']}
            rules={[{ required: true, message: '请输入向量数据库驱动路径' }]}
          >
            <Input placeholder="例如: ./backend/config_files/vector_db_driver/vec0.dll" />
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

export default VectorDbSettings;
