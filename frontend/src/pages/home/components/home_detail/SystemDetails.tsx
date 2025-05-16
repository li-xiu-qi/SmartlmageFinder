import React from 'react';
import { Row, Col, Card, Tooltip, Progress, Tag } from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  ClockCircleOutlined,
  HddOutlined, 
  DatabaseOutlined, 
  CloudOutlined
} from '@ant-design/icons';
import { SystemDetailsProps } from '../../types';

/**
 * 将秒转换为可读的运行时间
 */
const formatUptime = (seconds: number): string => {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${days}天 ${hours}小时 ${minutes}分钟`;
};

/**
 * 系统详情组件
 * 显示系统信息、存储信息、数据库状态、缓存状态和API状态
 */
const SystemDetails: React.FC<SystemDetailsProps> = ({ systemStatus }) => {
  if (!systemStatus) return null;

  return (
    <div className="system-details">
      <h2 className="section-title">系统详情</h2>
      <Row gutter={[16, 16]}>
        {/* 系统基本信息 */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card title="系统信息" size="small">
            <p><strong>版本：</strong> {systemStatus.system.version}</p>
            <p>
              <strong>运行时间：</strong> 
              <Tooltip title={formatUptime(systemStatus.system.uptime)}>
                <span><ClockCircleOutlined /> {Math.floor(systemStatus.system.uptime / 86400)}天</span>
              </Tooltip>
            </p>
            <p><strong>平台：</strong> {systemStatus.system.platform}</p>
            <p><strong>Python版本：</strong> {systemStatus.system.python_version}</p>
          </Card>
        </Col>

        {/* 存储信息 */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card title="存储信息" size="small">
            <p><strong>存储路径：</strong> {systemStatus.storage.upload_dir}</p>
            <p><strong>总存储：</strong> {(systemStatus.storage.total_size_mb / 1024).toFixed(2)} GB</p>
            <HddOutlined /> 存储使用
            <Progress 
              percent={Math.min(100, Math.round(systemStatus.storage.total_size_mb / 100000 * 100))} 
              size="small"
              status={systemStatus.storage.total_size_mb > 80000 ? "exception" : "normal"}
            />
          </Card>
        </Col>

        {/* 数据库状态 */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card title="数据库状态" size="small">
            <p>
              <strong>状态：</strong>
              {systemStatus.components.database.status === 'connected' ? (
                <Tag color="green"><CheckCircleOutlined /> 已连接</Tag>
              ) : (
                <Tag color="red"><CloseCircleOutlined /> 未连接</Tag>
              )}
            </p>            <p><strong>类型：</strong> {systemStatus.components.database.type || 'SQLite'}</p>
            <p><strong>路径：</strong> {systemStatus.components.database.path || 'N/A'}</p>
          </Card>
        </Col>

        {/* 缓存状态 */}
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card title="缓存状态" size="small">
            <p>
              <strong>状态：</strong>
              {systemStatus.cache?.enabled ? (
                <Tag color="green"><CheckCircleOutlined /> 已启用</Tag>
              ) : (
                <Tag color="orange"><CloseCircleOutlined /> 未启用</Tag>
              )}
            </p>
            <p><DatabaseOutlined /> 文本向量缓存: {systemStatus.cache?.text_vector_cache?.entries || 0}项 
               ({systemStatus.cache?.text_vector_cache?.size_mb || 0}MB)</p>
            <p><CloudOutlined /> 图像向量缓存: {systemStatus.cache?.image_vector_cache?.entries || 0}项 
               ({systemStatus.cache?.image_vector_cache?.size_mb || 0}MB)</p>
          </Card>
        </Col>

        {/* API状态 */}
        <Col xs={24} sm={12} md={8} lg={8}>
          <Card title="多模态API状态" size="small">
            <p>
              <strong>状态：</strong>
              {systemStatus.components.multimodal_api?.status === 'enabled' ? (
                <Tag color="green"><CheckCircleOutlined /> 已启用</Tag>
              ) : (
                <Tag color="red"><CloseCircleOutlined /> 未启用</Tag>
              )}
            </p>
            <p><strong>当前模型：</strong> {systemStatus.components.multimodal_api?.model || 'N/A'}</p>
            <p><strong>可用模型：</strong></p>
            <div>
              {systemStatus.components.multimodal_api?.available_models?.map((model: string) => (
                <Tag key={model} color="blue">{model}</Tag>
              )) || <Tag color="red">无可用模型</Tag>}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SystemDetails;
