import React from 'react';
import { Card, Row, Col, Badge } from 'antd';
import { SystemStatusData } from '@/types/system';

interface SystemStatusProps {
  systemStatus: SystemStatusData;
}

// 获取状态标签
const getStatusBadge = (status: string) => {
  const statusMap: Record<string, any> = {
    'healthy': { status: 'success', text: '正常' },
    'connected': { status: 'success', text: '已连接' },
    'available': { status: 'success', text: '可用' },
    'enabled': { status: 'success', text: '已启用' },
    'warning': { status: 'warning', text: '警告' },
    'disconnected': { status: 'error', text: '未连接' },
    'missing': { status: 'error', text: '缺失' },
    'error': { status: 'error', text: '错误' },
    'disabled': { status: 'default', text: '已禁用' }
  };
  
  const config = statusMap[status] || { status: 'default', text: status };
  
  return <Badge status={config.status as any} text={config.text} />;
};

const SystemStatus: React.FC<SystemStatusProps> = ({ systemStatus }) => {
  if (!systemStatus) return null;
  
  // 获取数据库文件名
  const getFileName = (path: string) => {
    if (!path) return '';
    // 同时处理 / 和 \ 分隔符，适应不同操作系统
    const parts = path.split(/[/\\]/);
    return parts[parts.length - 1];
  };
  
  return (
    <Card title="系统状态" style={{ marginBottom: 16 }}>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Card size="small" title="系统">
            <p><strong>版本:</strong> {systemStatus.system.version}</p>
            <p><strong>状态:</strong> {getStatusBadge(systemStatus.system.status)}</p>
            <p><strong>平台:</strong> {systemStatus.system.platform}</p>
            <p><strong>Python版本:</strong> {systemStatus.system.python_version}</p>
            <p><strong>运行时间:</strong> {Math.floor(systemStatus.system.uptime / 86400)}天 {Math.floor((systemStatus.system.uptime % 86400) / 3600)}时 {Math.floor((systemStatus.system.uptime % 3600) / 60)}分</p>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small" title="数据库与API">
            <p><strong>数据库状态:</strong> {getStatusBadge(systemStatus.components.database.status)}</p>
            <p><strong>数据库类型:</strong> {systemStatus.components.database.type}</p>
            <p><strong>向量驱动:</strong> {getStatusBadge(systemStatus.components.vector_db_driver.status)}</p>
            <p><strong>多模态API:</strong> {getStatusBadge(systemStatus.components.multimodal_api.status)}</p>
            <p><strong>当前模型:</strong> {systemStatus.components.multimodal_api.model}</p>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small" title="存储与缓存">
            <p><strong>图片总数:</strong> {systemStatus.storage.total_images}</p>
            <p><strong>标签总数:</strong> {systemStatus.storage.total_tags}</p>
            <p><strong>存储大小:</strong> {systemStatus.storage.total_size_mb.toFixed(2)} MB</p>
            <p><strong>文本向量缓存:</strong> {systemStatus.cache.text_vector_cache.entries}条 ({systemStatus.cache.text_vector_cache.size_mb.toFixed(2)} MB)</p>
            <p><strong>图像向量缓存:</strong> {systemStatus.cache.image_vector_cache.entries}条 ({systemStatus.cache.image_vector_cache.size_mb.toFixed(2)} MB)</p>
          </Card>
        </Col>
      </Row>
    </Card>
  );
};

export default SystemStatus;
