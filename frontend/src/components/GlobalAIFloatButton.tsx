/**
 * 全局AI推荐悬浮按钮组件
 * 提供AI图片推荐功能的全局访问
 */

import React, { useState } from 'react';
import { 
  FloatButton, 
  Drawer, 
  Button, 
  Input, 
  Card, 
  Empty, 
  Typography,
  Space,
  Row,
  Col,
  Image,
  Tag
} from 'antd';
import { 
  RobotOutlined, 
  SearchOutlined, 
  ClearOutlined,
  FireOutlined,
  HeartOutlined,
  EyeOutlined,
  PictureOutlined
} from '@ant-design/icons';
import { useAIRecommendation } from '@/hooks/useAIRecommendation';
import { SearchImageItem } from '@/types/models';

const { Text, Title } = Typography;
const { Search } = Input;

/**
 * 快速推荐问题配置
 */
const QUICK_RECOMMEND_QUERIES = [
  { icon: <FireOutlined />, text: '热门图片', query: '热门的图片' },
  { icon: <HeartOutlined />, text: '美丽风景', query: '美丽的自然风景' },
  { icon: <EyeOutlined />, text: '创意设计', query: '创意设计作品' },
  { icon: <PictureOutlined />, text: '艺术摄影', query: '艺术摄影作品' }
];

/**
 * 全局AI推荐悬浮按钮组件
 */
export const GlobalAIFloatButton: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [searchValue, setSearchValue] = useState('');

  const { 
    loading, 
    recommendResults, 
    getRecommendations, 
    clearRecommendResults,
    cancelRequest
  } = useAIRecommendation();

  /**
   * 处理推荐搜索
   */
  const handleSearch = async (query: string) => {
    if (!query.trim()) return;
    await getRecommendations(query);
  };

  /**
   * 处理快速推荐按钮点击
   */
  const handleQuickRecommend = async (query: string) => {
    setSearchValue(query);
    await getRecommendations(query);
  };

  /**
   * 清除推荐结果
   */
  const handleClearResults = () => {
    clearRecommendResults();
    setSearchValue('');
  };

  /**
   * 渲染推荐结果
   */
  const renderRecommendResults = () => {
    if (!recommendResults) {
      return (
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="输入描述，让AI为您推荐相关图片"
          />
        </div>
      );
    }

    const { images, query_rewrite } = recommendResults;

    if (!images || images.length === 0) {
      return (
        <div style={{ textAlign: 'center', padding: '40px 20px' }}>
          <Empty
            description="没有找到相关图片"
          />
        </div>
      );
    }

    return (
      <div>
        {/* 查询优化信息 */}
        {query_rewrite && query_rewrite.rewrite_success && (
          <Card size="small" style={{ marginBottom: 16, backgroundColor: '#f6ffed' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              AI优化查询：{query_rewrite.original_query} → {query_rewrite.optimized_query}
            </Text>
          </Card>
        )}

        {/* 推荐结果 */}
        <div style={{ marginBottom: 16 }}>
          <Title level={5}>为您推荐 {images.length} 张图片</Title>
        </div>

        <Row gutter={[8, 8]}>
          {images.map((item: SearchImageItem) => (
            <Col span={12} key={item.id}>
              <Card
                size="small"
                hoverable
                cover={
                  <div style={{ height: 120, overflow: 'hidden' }}>
                    <Image
                      src={item.filepath}
                      alt={item.title}
                      style={{ 
                        width: '100%', 
                        height: '100%', 
                        objectFit: 'cover' 
                      }}
                      preview={{
                        src: item.filepath
                      }}
                    />
                  </div>
                }
              >
                <Card.Meta
                  title={
                    <Text 
                      ellipsis={{ tooltip: item.title }} 
                      style={{ fontSize: '12px' }}
                    >
                      {item.title}
                    </Text>
                  }
                  description={
                    <div>
                      {item.description && (
                        <Text 
                          type="secondary" 
                          ellipsis={{ tooltip: item.description }}
                          style={{ fontSize: '11px' }}
                        >
                          {item.description}
                        </Text>
                      )}
                      {item.score !== undefined && (
                        <div style={{ marginTop: 4 }}>
                          <Tag color="blue" style={{ fontSize: '10px' }}>
                            相关度: {(item.score * 100).toFixed(1)}%
                          </Tag>
                        </div>
                      )}
                    </div>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      </div>
    );
  };

  return (
    <>
      <FloatButton
        icon={<RobotOutlined />}
        tooltip="AI图片推荐"
        onClick={() => setOpen(true)}
        style={{ 
          right: 24, 
          bottom: 24,
          width: 60,
          height: 60
        }}
      />

      <Drawer
        title={
          <Space>
            <RobotOutlined />
            AI图片推荐助手
          </Space>
        }
        placement="right"
        onClose={() => setOpen(false)}
        open={open}
        width={400}
        extra={
          <Space>
            {loading && (
              <Button 
                icon={<ClearOutlined />} 
                size="small" 
                onClick={cancelRequest}
                danger
              >
                取消
              </Button>
            )}
            {recommendResults && !loading && (
              <Button 
                icon={<ClearOutlined />} 
                size="small" 
                onClick={handleClearResults}
              >
                清除结果
              </Button>
            )}
          </Space>
        }
      >
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          {/* 搜索区域 */}
          <div style={{ marginBottom: 16 }}>
            <Search
              placeholder="描述您想要找的图片..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              onSearch={handleSearch}
              loading={loading}
              enterButton={<SearchOutlined />}
              size="large"
            />
            
            {/* 加载状态提示 */}
            {loading && (
              <div style={{ 
                marginTop: 8, 
                padding: '8px 12px', 
                backgroundColor: '#f0f9ff', 
                border: '1px solid #b3d8ff', 
                borderRadius: '4px',
                textAlign: 'center'
              }}>
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  🤖 AI正在分析您的需求并搜索相关图片，请耐心等待...
                </Text>
              </div>
            )}
          </div>

          {/* 快速推荐按钮 */}
          {!recommendResults && (
            <div style={{ marginBottom: 24 }}>
              <Title level={5} style={{ marginBottom: 12 }}>快速推荐</Title>
              <Space wrap>
                {QUICK_RECOMMEND_QUERIES.map((item, index) => (
                  <Button
                    key={index}
                    icon={item.icon}
                    size="small"
                    onClick={() => handleQuickRecommend(item.query)}
                    loading={loading}
                  >
                    {item.text}
                  </Button>
                ))}
              </Space>
            </div>
          )}

          {/* 推荐结果区域 */}
          <div style={{ flex: 1, overflow: 'auto' }}>
            {renderRecommendResults()}
          </div>
        </div>
      </Drawer>
    </>
  );
};

export default GlobalAIFloatButton;
