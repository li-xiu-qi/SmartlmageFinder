import React from 'react';
import { Card, Form, Input, Row, Col, Tooltip, Alert, Badge } from 'antd';
import { InfoCircleOutlined, DatabaseOutlined } from '@ant-design/icons';
import { SystemStatusData } from '@/types/system';

interface VectorDbSettingsProps {
  systemStatus?: SystemStatusData | null;
  loading?: boolean;
}

const VectorDbSettings: React.FC<VectorDbSettingsProps> = ({ 
  systemStatus,
  loading = false
}) => {  // 获取向量数据库状态
  const driverStatus = systemStatus?.components.vector_db_driver.status || 'unknown';
  // 获取驱动路径
  const driverPath = systemStatus?.components.vector_db_driver.path || '';
  // 状态映射
  const statusMap: Record<string, { status: 'success' | 'error' | 'default' | 'warning' | 'processing'; text: string }> = {
    'available': { status: 'success', text: '正常' },
    'missing': { status: 'error', text: '未找到' },
    'error': { status: 'error', text: '错误' },
    'unknown': { status: 'default', text: '未知' }
  };
  
  const driverStatusInfo = statusMap[driverStatus] || statusMap.unknown;
  
  return (
    <Card 
      title={
        <span>
          向量数据库设置 
          <Tooltip title="配置向量数据库驱动，用于存储和检索向量数据">
            <InfoCircleOutlined style={{ marginLeft: 8, color: '#1890ff' }} />
          </Tooltip>
          {driverStatus && (
            <Badge 
              status={driverStatusInfo.status} 
              text={driverStatusInfo.text}
              style={{ marginLeft: 16 }}
            />
          )}
        </span>
      } 
      style={{ marginBottom: 16 }}
    >
      {driverStatus === 'error' && systemStatus?.components.vector_db_driver.error && (
        <Alert
          message="向量数据库驱动错误"
          description={systemStatus.components.vector_db_driver.error}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      <Row>
        <Col span={24}>          <Form.Item 
            label="驱动路径" 
            name={['vectorDb', 'driverPath']}
            rules={[{ required: true, message: '请输入向量数据库驱动路径' }]}
            tooltip="向量数据库驱动文件的路径，通常为.dll或.so文件"
            initialValue={driverPath}
            extra="更改此设置后需要重启服务才能生效"
          >
            <Input 
              placeholder="例如: ./backend/config_files/vector_db_driver/vec0.dll" 
              disabled={loading}
              prefix={<DatabaseOutlined />}
              title={driverPath} // 添加完整路径的悬停提示
            />
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

export default VectorDbSettings;
