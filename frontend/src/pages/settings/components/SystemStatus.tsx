import React from 'react';
import { Card, Row, Col, Badge, Tooltip, Statistic } from 'antd';
import { InfoCircleOutlined, DatabaseOutlined, CloudOutlined, SettingOutlined } from '@ant-design/icons';
import { SystemStatusData } from '@/types/system';

interface SystemStatusProps {
  systemStatus: SystemStatusData;
}

// 获取状态标签
const getStatusBadge = (status: string) => {
  const statusMap: Record<string, { status: 'success' | 'warning' | 'error' | 'default'; text: string }> = {
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
  
  return <Badge status={config.status} text={config.text} />;
};

const SystemStatus: React.FC<SystemStatusProps> = ({ systemStatus }) => {
  if (!systemStatus) return null;
  
  return (
    <Card 
      title={
        <span>
          系统状态
          <Tooltip title="显示系统各组件的运行状态与配置信息">
            <InfoCircleOutlined style={{ marginLeft: 8, color: '#1890ff' }} />
          </Tooltip>
        </span>
      } 
      style={{ marginBottom: 16 }}
    >
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Card 
            size="small" 
            title={
              <span>
                <SettingOutlined /> 系统
              </span>
            }
            bordered={false}
            className="status-card"
          >
            <p><strong>版本:</strong> {systemStatus.system.version}</p>
            <p><strong>状态:</strong> {getStatusBadge(systemStatus.system.status)}</p>
            <p><strong>平台:</strong> {systemStatus.system.platform}</p>
            <p><strong>Python版本:</strong> {systemStatus.system.python_version}</p>
            <p><strong>应用运行时间:</strong> {systemStatus.system.app_uptime_formatted}</p>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card 
            size="small" 
            title={
              <span>
                <DatabaseOutlined /> 数据库与API
              </span>
            }
            bordered={false}
            className="status-card"
          >
            <p><strong>数据库状态:</strong> {getStatusBadge(systemStatus.components.database.status)}</p>
            <p><strong>数据库类型:</strong> {systemStatus.components.database.type}</p>
            <p><strong>数据表计数:</strong> {Object.keys(systemStatus.components.database.tables_info || {}).length} 个表</p>
            <p><strong>向量驱动:</strong> {getStatusBadge(systemStatus.components.vector_db_driver.status)}</p>
            <p><strong>多模态API:</strong> {getStatusBadge(systemStatus.components.multimodal_api.status)}</p>
            <p><strong>当前模型:</strong> {systemStatus.components.multimodal_api.model}</p>
            <p><strong>可用模型数:</strong> {systemStatus.components.multimodal_api.available_models?.length || 0}</p>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card 
            size="small" 
            title={
              <span>
                <CloudOutlined /> 存储与缓存
              </span>
            }
            bordered={false}
            className="status-card"
          >
            <Row gutter={[8, 16]}>
              <Col span={12}>
                <Statistic 
                  title="图片总数" 
                  value={systemStatus.storage.total_images} 
                  suffix="张" 
                  groupSeparator="," 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="标签总数" 
                  value={systemStatus.storage.total_tags} 
                  suffix="个" 
                  groupSeparator="," 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="存储大小" 
                  value={systemStatus.storage.total_size_mb} 
                  precision={2} 
                  suffix="MB" 
                />
              </Col>
              <Col span={12}>
                <Statistic 
                  title="缓存大小" 
                  value={systemStatus.cache.total_size_mb} 
                  precision={2} 
                  suffix="MB" 
                />
              </Col>            </Row>
            <div className="cache-info">
              <p><strong>缓存总条目:</strong> {systemStatus.cache.total_entries}条</p>
              <p><strong>文本向量缓存:</strong> {systemStatus.cache.text_vector_cache.entries}条 ({systemStatus.cache.text_vector_cache.size_mb.toFixed(2)} MB)</p>
              <p><strong>图像向量缓存:</strong> {systemStatus.cache.image_vector_cache.entries}条 ({systemStatus.cache.image_vector_cache.size_mb.toFixed(2)} MB)</p>
            </div>
          </Card>
        </Col>
      </Row>
    </Card>
  );
};

export default SystemStatus;
