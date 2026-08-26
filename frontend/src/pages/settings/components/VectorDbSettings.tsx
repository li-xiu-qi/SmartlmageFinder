import React from 'react';
import { Card, Form, Input, Row, Col, Tooltip, Alert, Badge, Tag, Descriptions } from 'antd';
import { InfoCircleOutlined, DatabaseOutlined, RobotOutlined } from '@ant-design/icons';
import { SystemStatusData } from '@/types/system';
import { useVectorCapability } from '@/hooks/useVectorCapability';

interface VectorDbSettingsProps {
  systemStatus?: SystemStatusData | null;
  loading?: boolean;
}

const VectorDbSettings: React.FC<VectorDbSettingsProps> = ({ 
  systemStatus,
  loading = false
}) => {
  // 获取向量数据库状态
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

  // 向量引擎能力状态
  const { vectorEnabled, status: vectorEngineStatus } = useVectorCapability();

  return (
    <Card 
      title={
        <span>
          向量数据库设置 
          <Tooltip 
            title="配置向量数据库驱动和 Embedding 模型，用于存储和检索向量数据"
            getPopupContainer={(trigger) => trigger.parentElement || document.body}
          >
            <InfoCircleOutlined style={{ marginLeft: 8, color: '#1890ff' }} />
          </Tooltip>
          <Badge 
            status={vectorEnabled ? 'success' : 'warning'} 
            text={vectorEnabled ? '语义搜索可用' : '语义搜索不可用'}
            style={{ marginLeft: 16 }}
          />
        </span>
      } 
      style={{ marginBottom: 16 }}
    >
      {/* 综合能力提示 */}
      {!vectorEnabled && (
        <Alert
          message="语义搜索暂不可用"
          description={
            <>
              {vectorEngineStatus?.driver.error && <div>驱动: {vectorEngineStatus.driver.error}</div>}
              {vectorEngineStatus?.model.error && <div>模型: {vectorEngineStatus.model.error}</div>}
              <div style={{ marginTop: 4, color: '#888' }}>配置驱动和模型后重启服务即可启用。模糊搜索不受影响。</div>
            </>
          }
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}
      
      {/* 驱动状态 */}
      <Descriptions size="small" column={1} style={{ marginBottom: 16 }} bordered>
        <Descriptions.Item label="sqlite-vec 驱动">
          {driverStatusInfo && (
            <Badge status={driverStatusInfo.status} text={driverStatusInfo.text} />
          )}
          {driverPath && (
            <span style={{ marginLeft: 8, color: '#888', fontSize: 12 }}>{driverPath}</span>
          )}
        </Descriptions.Item>
        <Descriptions.Item label="Embedding 模型">
          {vectorEngineStatus?.model.available ? (
            <Tag color="success" icon={<RobotOutlined />}>已加载</Tag>
          ) : (
            <Tag color="warning" icon={<RobotOutlined />}>未配置</Tag>
          )}
          {vectorEngineStatus?.model.path && (
            <span style={{ marginLeft: 8, color: '#888', fontSize: 12 }}>
              {vectorEngineStatus.model.path}
              {vectorEngineStatus.model.dimension > 0 && ` (${vectorEngineStatus.model.dimension}维)`}
            </span>
          )}
        </Descriptions.Item>
      </Descriptions>

      {/* 驱动路径配置 */}
      <Row>
        <Col span={24}>
          <Form.Item 
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
              title={driverPath}
            />
          </Form.Item>
        </Col>
      </Row>
    </Card>
  );
};

export default VectorDbSettings;
