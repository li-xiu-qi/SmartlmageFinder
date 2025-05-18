import React from 'react';
import { Row, Col, Card, Tag } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { SystemDetailsProps } from '../../types';

/**
 * 系统详情组件
 * 简化版本 - 当前未在首页使用
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
            <p><strong>状态：</strong> 
              {systemStatus.system.status === 'online' ? (
                <Tag color="green"><CheckCircleOutlined /> 在线</Tag>
              ) : (
                <Tag color="red"><CloseCircleOutlined /> 离线</Tag>
              )}
            </p>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SystemDetails;
};

export default SystemDetails;
