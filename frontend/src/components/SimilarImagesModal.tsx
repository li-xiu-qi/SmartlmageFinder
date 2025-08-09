import React, { useState } from 'react';
import { Select, Button, Row, Col, Card, Tag, Spin, Empty, Typography } from 'antd';
import { SearchOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { ImageSearchResult } from '@/types/models';
import { getImageUrl } from '@/utils/typeConverters';
import { VectorType } from '@/types/search'; // Changed from VectorSearchTarget to VectorType
import RefModal from '@/components/RefModal';
import ImagePreview from '@/components/ImagePreview';

const { Option } = Select;

// 定义搜索类型选项，使用 VectorType
const searchTypeOptions = [
  { value: VectorType.IMAGE, label: '图像向量' },
  { value: VectorType.TITLE, label: '标题向量' },
  { value: VectorType.DESCRIPTION, label: '描述向量' },
];

interface SimilarImagesModalProps {
  open: boolean;
  onClose: () => void;
  loading: boolean;
  searchTarget: VectorType; // Changed from VectorSearchTarget to VectorType
  onSearchTargetChange: (value: VectorType) => void; // Changed from VectorSearchTarget to VectorType
  onSearch: () => void;
  similarImages: ImageSearchResult[];
}

/**
 * 相似图片展示模态框
 */
const SimilarImagesModal: React.FC<SimilarImagesModalProps> = ({
  open,
  onClose,
  loading,
  searchTarget,
  onSearchTargetChange,
  onSearch,
  similarImages
}) => {
  const [selectedPreviewImage, setSelectedPreviewImage] = useState<ImageSearchResult | null>(null);

  const handleImageClick = (image: ImageSearchResult) => {
    setSelectedPreviewImage(image);
  };

  const handleBackToList = () => {
    setSelectedPreviewImage(null);
  };

  return (
    <RefModal
      title={`相似图片 (基于${searchTypeOptions.find(opt => opt.value === searchTarget)?.label || '图像向量'})`}
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
      destroyOnHidden
    >
      <div style={{ marginBottom: 16 }}>
        <Select
          value={searchTarget}
          onChange={onSearchTargetChange}
          style={{ width: 150, marginRight: 16 }}
        >
          {searchTypeOptions.map(option => (
            <Option key={option.value} value={option.value}>{option.label}</Option>
          ))}
        </Select>

        <Button
          type="primary"
          icon={<SearchOutlined />}
          onClick={onSearch}
          loading={loading}
        >
          重新搜索
        </Button>
      </div>

      {selectedPreviewImage ? (
        <div>
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={handleBackToList}
            style={{ marginBottom: 16 }}
          >
            返回列表
          </Button>
          <ImagePreview image={selectedPreviewImage as any} />
          <Typography.Title level={4} style={{ marginTop: 16 }}>{selectedPreviewImage.title}</Typography.Title>
          <div style={{ marginTop: 8 }}>
            {selectedPreviewImage.score !== undefined ?
              `相关度: ${Math.round(selectedPreviewImage.score * 100)}%` :
              selectedPreviewImage.distance !== undefined ?
                `距离: ${selectedPreviewImage.distance.toFixed(4)}` :
                '相似度: N/A'}
          </div>
          <div style={{ marginTop: 8 }}>
            {selectedPreviewImage.tags.map(tag => (
              <Tag key={tag} style={{ marginRight: 4 }}>{tag}</Tag>
            ))}
          </div>
        </div>
      ) : loading ? (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" />
          <p style={{ marginTop: 16 }}>正在查找相似图片，请稍候...</p>
        </div>
      ) : similarImages.length > 0 ? (
        <Row gutter={[16, 16]}>
          {similarImages.map(img => (
            <Col xs={12} sm={8} md={8} key={img.id}>
              <Card
                hoverable
                onClick={() => handleImageClick(img)} // Add onClick handler
                cover={
                  <div style={{ height: 160, overflow: 'hidden' }}>
                    <img
                      alt={img.title}
                      src={getImageUrl(img as any)}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  </div>
                }
                size="small"
              >
                <Card.Meta
                  title={img.title}
                  description={
                    <>
                      <div>
                        {img.score !== undefined ?
                          `相关度: ${Math.round(img.score * 100)}%` :
                          img.distance !== undefined ?
                            `距离: ${img.distance.toFixed(4)}` :
                            '相似度: N/A'}
                      </div>
                      <div style={{ marginTop: 4 }}>
                        {img.tags.slice(0, 2).map(tag => (
                          <Tag key={tag} style={{ marginRight: 4 }}>{tag}</Tag>
                        ))}
                        {img.tags.length > 2 && <Tag>...</Tag>}
                      </div>
                    </>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      ) : (
        <Empty description="未找到相似图片" />)}
    </RefModal>
  );
};

export default SimilarImagesModal;
