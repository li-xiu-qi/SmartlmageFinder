import React from 'react';
import { Typography, Descriptions } from 'antd';
import { ImageDetail } from '@/types';

const { Title } = Typography;

interface MetadataSectionProps {
  metadata: Record<string, any>;
}

/**
 * 元数据展示组件
 */
const MetadataSection: React.FC<MetadataSectionProps> = ({ metadata }) => {
  const metadataEntries = Object.entries(metadata || {});

  if (metadataEntries.length === 0) {
    return (
      <div className="detail-section">
        <Title level={5} className="section-title">元数据</Title>
        <p>暂无元数据</p>
      </div>
    );
  }

  return (
    <div className="detail-section">
      <Title level={5} className="section-title">元数据</Title>
      <Descriptions bordered column={1} size="small">
        {metadataEntries.map(([key, value]) => (
          <Descriptions.Item key={key} label={key}>
            {value}
          </Descriptions.Item>
        ))}
      </Descriptions>
    </div>
  );
};

export default MetadataSection;
