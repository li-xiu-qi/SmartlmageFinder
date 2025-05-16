import React from 'react';
import { Card, Statistic, Row, Col } from 'antd';
import { CheckCircleOutlined, WarningOutlined, PictureOutlined, TagsOutlined } from '@ant-design/icons';
import { StatusCardsProps } from '../../types';

/**
 * 首页状态卡片组件
 * 显示系统状态、图片总数和标签总数
 */
const StatusCards: React.FC<StatusCardsProps> = ({ stats }) => {
  return (
    <Row gutter={16} className="gutter-row">
      <Col xs={24} sm={8}>
        <Card className="stat-card">
          <Statistic
            title="系统状态"
            value={stats.status === 'healthy' ? '正常' : '异常'}
            valueStyle={{ color: stats.status === 'healthy' ? '#3f8600' : '#cf1322' }}
            prefix={stats.status === 'healthy' ? <CheckCircleOutlined /> : <WarningOutlined />}
          />
        </Card>
      </Col>
      <Col xs={24} sm={8}>
        <Card className="stat-card">
          <Statistic
            title="图片总数"
            value={stats.totalImages}
            prefix={<PictureOutlined />}
          />
        </Card>
      </Col>
      <Col xs={24} sm={8}>
        <Card className="stat-card">
          <Statistic
            title="标签总数"
            value={stats.totalTags}
            prefix={<TagsOutlined />}
          />
        </Card>
      </Col>
    </Row>
  );
};

export default StatusCards;
