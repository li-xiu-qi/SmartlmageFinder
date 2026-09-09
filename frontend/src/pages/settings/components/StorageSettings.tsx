import React from 'react';
import { Card, Form, Input, InputNumber, Button, Typography, Row, Col, Tooltip, Statistic, Skeleton, Space } from 'antd';
import { ClearOutlined, FolderOpenOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { SystemStatusData } from '@/types/system';

const { Text } = Typography;

interface StorageSettingsProps {
  clearCacheLoading: boolean;
  onClearCache: () => void;
  systemStatus: SystemStatusData | null;
  loading?: boolean;
}

const StorageSettings: React.FC<StorageSettingsProps> = ({ 
  clearCacheLoading, 
  onClearCache,
  systemStatus,
  loading = false
}) => {
  // 从systemStatus获取缓存信息
  const totalCacheSize = systemStatus ? 
    systemStatus.cache.total_size_mb.toFixed(2) :
    "0.00";
    
  const hasCache = systemStatus ? systemStatus.cache.total_size_mb > 0 : false;

  const maxCachePercent = systemStatus && systemStatus.cache.max_size_gb > 0 ? 
    Math.min(100, (systemStatus.cache.total_size_mb / (systemStatus.cache.max_size_gb * 1024)) * 100).toFixed(1) : 
    "0.0";
    
  return (
    <Card 
      title={
        <span>
          存储设置 
          <Tooltip 
            title="配置图像数据和缓存的存储位置与策略"
            getPopupContainer={(trigger) => trigger.parentElement || document.body}
          >
            <InfoCircleOutlined style={{ marginLeft: 8, color: 'hsl(var(--primary))' }} />
          </Tooltip>
        </span>
      } 
      style={{ marginBottom: 16 }}
    >
      {loading ? (
        <Skeleton active paragraph={{ rows: 4 }} />
      ) : (
        <>
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item 
                label="存储根目录" 
                name={['storage', 'rootDirectory']}
                rules={[{ required: true, message: '请输入存储根目录' }]}
                tooltip="所有图像文件将存储在此目录下，更改目录不会自动迁移现有文件"
              >
                <Input 
                  placeholder="例如: ./data/images" 
                  disabled={loading}
                  prefix={<FolderOpenOutlined />} 
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item 
                label="缓存目录" 
                name={['storage', 'cacheDirectory']}
                rules={[{ required: true, message: '请输入缓存目录' }]}
                tooltip="系统缓存（包括向量缓存）的存储位置"
              >
                <Input 
                  placeholder="例如: ./data/caches" 
                  disabled={loading}
                  prefix={<FolderOpenOutlined />} 
                />
              </Form.Item>
            </Col>
          </Row>
          <Row gutter={24}>
            <Col span={12}>
              <Form.Item 
                label="最大缓存大小 (GB)" 
                name={['storage', 'maxCacheSize']}
                rules={[{ required: true, message: '请输入最大缓存大小' }]}
                tooltip="设置系统缓存的最大占用空间，超过此大小会自动清理最旧的缓存"
              >
                <InputNumber 
                  min={0.5} 
                  max={10} 
                  step={0.5} 
                  style={{ width: '100%' }} 
                  disabled={loading}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <div style={{ marginTop: 29 }}>
                <Space>
                  <Button 
                    type="primary" 
                    danger 
                    icon={<ClearOutlined />} 
                    onClick={onClearCache}
                    loading={clearCacheLoading}
                    disabled={!hasCache}
                  >
                    清除缓存
                  </Button>
                  <div>
                    <Text type="secondary">
                      当前缓存: {totalCacheSize} MB 
                      {systemStatus?.cache.max_size_gb ? ` (${maxCachePercent}%)` : ''}
                    </Text>
                    <br />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      清除后需重新生成向量，短期内可能影响搜索性能
                    </Text>
                  </div>
                </Space>
              </div>
            </Col>
          </Row>
          {systemStatus && (
            <Row gutter={24} style={{ marginTop: 16 }}>
              <Col span={8}>
                <Statistic 
                  title="图片总数" 
                  value={systemStatus.storage.total_images} 
                  suffix="张" 
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="存储大小" 
                  value={systemStatus.storage.total_size_mb.toFixed(2)} 
                  suffix="MB" 
                />
              </Col>
              <Col span={8}>
                <Statistic 
                  title="标签总数" 
                  value={systemStatus.storage.total_tags} 
                  suffix="个" 
                />
              </Col>
            </Row>
          )}
        </>
      )}
    </Card>
  );
};

export default StorageSettings;
