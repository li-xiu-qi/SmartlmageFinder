import React from 'react';
import { Card, Space, Divider, Typography } from 'antd';

const { Text, Title } = Typography;

export interface SearchMetaBarProps {
  total: number;
  searchTime: number; // ms
  referenceImage?: { id: number; title: string };
}

/**
 * 搜索元信息条：展示结果数量 / 耗时 / 参照图
 */
const SearchMetaBar: React.FC<SearchMetaBarProps> = ({ total, searchTime, referenceImage }) => {
  return (
    <Card className="search-results-header">
      <Space direction="vertical" size="small">
        <Title level={5}>搜索结果</Title>
        <Space split={<Divider type="vertical" />}>
          <Text>共找到 {total} 张相关图片</Text>
          <Text>耗时 {(searchTime / 1000).toFixed(2)} 秒</Text>
          {referenceImage && <Text>参照图: {referenceImage.title}</Text>}
        </Space>
      </Space>
    </Card>
  );
};

export default SearchMetaBar;
