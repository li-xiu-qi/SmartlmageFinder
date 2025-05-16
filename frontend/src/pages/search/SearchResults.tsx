import React from 'react';
import { Empty, Row, Col, Card, Spin, Typography, Space, Divider } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import ImageCard from '@/pages/images/components/ImageCard';
import { SearchImageItem } from '@/types/models';

const { Text, Title } = Typography;

interface SearchResultsProps {
  loading: boolean;
  results: SearchImageItem[];
  total: number;
  searchTime: number;
  searchKeyword?: string;
}

/**
 * 搜索结果组件
 */
const SearchResults: React.FC<SearchResultsProps> = ({
  loading,
  results,
  total,
  searchTime,
  searchKeyword
}) => {
  if (loading) {
    return (
      <div className="search-loading-container">
        <Spin indicator={<LoadingOutlined style={{ fontSize: 36 }} spin />} />
        <p>正在搜索，请稍候...</p>
      </div>
    );
  }

  // 如果没有搜索结果
  if (results.length === 0) {
    return (
      <Card className="search-results-empty">
        <Empty 
          description={
            <span>
              {searchKeyword 
                ? `没有找到与 "${searchKeyword}" 相关的图片`
                : "请输入关键词或上传图片进行搜索"}
            </span>
          }
        />
      </Card>
    );
  }

  return (
    <div className="search-results-container">
      <Card className="search-results-header">
        <Space direction="vertical" size="small">
          <Title level={5}>搜索结果</Title>
          <Space split={<Divider type="vertical" />}>
            <Text>共找到 {total} 张相关图片</Text>
            <Text>耗时 {(searchTime / 1000).toFixed(2)} 秒</Text>
          </Space>
        </Space>
      </Card>
      
      <Row gutter={[16, 16]} className="search-results-grid">
        {results.map(image => (
          <Col xs={24} sm={12} md={8} lg={6} key={image.id}>            <ImageCard 
              image={image} 
              showSimilarity={true}
            />
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default SearchResults;
