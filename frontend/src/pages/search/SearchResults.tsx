import React, { useState, useEffect } from 'react';
import { Empty, Row, Col, Card, Spin, Typography, Space, Divider, Drawer, message } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import ImageCard from '@/pages/images/components/ImageCard';
import SharedImageDetail from '@/components/SharedImageDetail';
import { imageService } from '@/services/api';
import { SearchImageItem } from '@/types/models';
import { ImageDetail } from '@/types';
import './styles/SearchResults.less'; // 导入新的样式文件

const { Text, Title } = Typography;

interface SearchResultsProps {
  loading: boolean;
  results: SearchImageItem[];
  total: number;
  searchTime: number;
  searchKeyword?: string;
  referenceImage?: {
    id: number;
    title: string;
  };
}

/**
 * 搜索结果组件
 */
const SearchResults: React.FC<SearchResultsProps> = ({
  loading,
  results: initialResults,
  total,
  searchTime,
  searchKeyword,
  referenceImage
}) => {
  const [selectedImage, setSelectedImage] = useState<ImageDetail | null>(null);
  const [isDrawerVisible, setIsDrawerVisible] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [currentResults, setCurrentResults] = useState<SearchImageItem[]>(initialResults);

  useEffect(() => {
    setCurrentResults(initialResults);
  }, [initialResults]);

  const handleImageClick = async (imageItem: SearchImageItem) => {
    setDrawerLoading(true);
    setIsDrawerVisible(true);
    try {
      const response = await imageService.getImageDetail({ image_id: imageItem.id });
      if (response.status === 'success' && response.data) {
        setSelectedImage(response.data);
      } else {
        message.error('加载图片详情失败');
        setIsDrawerVisible(false);
      }
    } catch (error) {
      console.error('获取图片详情失败:', error);
      message.error('加载图片详情失败');
      setIsDrawerVisible(false);
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleDrawerClose = () => {
    setIsDrawerVisible(false);
    setSelectedImage(null);
  };

  const handleImageUpdate = (updatedImage: ImageDetail) => {
    setSelectedImage(updatedImage);
    setCurrentResults(prevResults => 
      prevResults.map(item => 
        item.id === updatedImage.id 
          ? { ...item, title: updatedImage.title } 
          : item
      )
    );
  };

  const handleImageDelete = (deletedImageId: number) => {
    setIsDrawerVisible(false);
    setSelectedImage(null);
    setCurrentResults(prevResults => prevResults.filter(item => item.id !== deletedImageId));
    message.success('图片已删除');
  };

  if (loading) {
    return (
      <div className="search-loading-container">
        <Spin indicator={<LoadingOutlined style={{ fontSize: 36 }} spin />} />
        <p>正在搜索，请稍候...</p>
      </div>
    );
  }

  // 如果没有搜索结果
  if (currentResults.length === 0 && !loading) {
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
            {referenceImage && (
              <Text>参照图: {referenceImage.title}</Text>
            )}
          </Space>
        </Space>
      </Card>
      
      <Row gutter={[16, 16]} className="search-results-grid">
        {currentResults.map(image => (
          <Col xs={24} sm={12} md={8} lg={6} key={image.id} onClick={() => handleImageClick(image)}>
            <ImageCard 
              image={image} 
              showSimilarity={true}
            />
          </Col>
        ))}
      </Row>

      {selectedImage && (
        <Drawer
          title={selectedImage.title || "图片详情"}
          placement="right"
          width={640} // 修改宽度为 640
          onClose={handleDrawerClose}
          open={isDrawerVisible}
          destroyOnClose
        >
          {drawerLoading ? (
            <div className="drawer-loading-indicator"> {/* 使用 CSS 类替代内联样式 */}
              <Spin />
              <p>正在加载详情...</p>
            </div>
          ) : (
            <SharedImageDetail
              image={selectedImage}
              onUpdate={handleImageUpdate}
              onDelete={handleImageDelete}
              onClose={handleDrawerClose}
            />
          )}
        </Drawer>
      )}
    </div>
  );
};

export default SearchResults;
