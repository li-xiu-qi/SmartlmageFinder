import React from 'react';
import { Card, Statistic, Row, Col, Tooltip } from 'antd';
import { CheckCircleOutlined, WarningOutlined, PictureOutlined, TagsOutlined } from '@ant-design/icons';
import { StatusCardsProps } from '../../types';
import './styles.less';

/**
 * 首页状态卡片组件
 * 显示系统状态、图片总数和标签总数
 */
const StatusCards: React.FC<StatusCardsProps> = ({ stats }) => {
  return (
    <div className="status-cards-container">
      <h2 className="section-title">系统状态概览</h2>
      <Row gutter={[16, 16]} className="gutter-row">
        <Col xs={24} sm={8}>
          <Card className="stat-card" hoverable>
            <Tooltip title={stats.status === 'healthy' ? '系统正常运行中' : '系统存在异常，请检查'}>
              <Statistic
                title="系统状态"
                value={stats.status === 'healthy' ? '正常' : '异常'}
                valueStyle={{ color: stats.status === 'healthy' ? '#3f8600' : '#cf1322' }}
                prefix={stats.status === 'healthy' ? <CheckCircleOutlined /> : <WarningOutlined />}
              />
            </Tooltip>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="stat-card" hoverable>
            <Tooltip title={`系统目前共有 ${stats.totalImages} 张图片`}>
              <Statistic
                title="图片总数"
                value={stats.totalImages}
                prefix={<PictureOutlined />}
              />
            </Tooltip>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="stat-card" hoverable>
            <Tooltip title={`系统目前共有 ${stats.totalTags} 个标签`}>
              <Statistic
                title="标签总数"
                value={stats.totalTags}
                prefix={<TagsOutlined />}
              />
            </Tooltip>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default StatusCards;
