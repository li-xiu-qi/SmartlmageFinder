import React from 'react';
import { Modal, Select, Button, Row, Col, Card, Tag, Spin, Empty } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { ImageSearchResult } from '@/types';

const { Option } = Select;

// 定义搜索类型选项
const searchTypeOptions = [
  { value: 'image', label: '图像向量' },
  { value: 'title', label: '标题向量' },
  { value: 'description', label: '描述向量' },
];

interface SimilarImagesModalProps {
  open: boolean;
  onClose: () => void;
  loading: boolean;
  searchType: string;
  onSearchTypeChange: (value: string) => void;
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
  searchType,
  onSearchTypeChange,
  onSearch,
  similarImages
}) => {
  return (
    <Modal
      title={`相似图片 (基于${searchTypeOptions.find(opt => opt.value === searchType)?.label || '图像向量'})`}
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
      destroyOnClose
    >
      <div style={{ marginBottom: 16 }}>
        <Select
          value={searchType}
          onChange={onSearchTypeChange}
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

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" />
          <p style={{ marginTop: 16 }}>正在查找相似图片，请稍候...</p>
        </div>
      ) : similarImages.length > 0 ? (
        <Row gutter={[16, 16]}>
          {similarImages.map(img => (
            <Col xs={12} sm={8} md={8} key={img.uuid}>
              <Card
                hoverable
                cover={
                  <div style={{ height: 160, overflow: 'hidden' }}>
                    <img 
                      alt={img.title} 
                      src={img.filepath} 
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
                      <div>相似度: {Math.round(img.score * 100)}%</div>
                      {(img.score_components || img.similarity_components) && (
                        <div style={{ fontSize: '12px', color: '#888', marginTop: 2 }}>
                          {Object.entries(img.score_components || img.similarity_components || {}).map(([mode, score]) => (
                            <div key={mode}>
                              {mode === 'image' ? '图像' : mode === 'title' ? '标题' : mode === 'description' ? '描述' : mode}: 
                              {Math.round(score * 100)}%
                            </div>
                          ))}
                        </div>
                      )}
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
        <Empty description="未找到相似图片" />
      )}
    </Modal>
  );
};

export default SimilarImagesModal;
