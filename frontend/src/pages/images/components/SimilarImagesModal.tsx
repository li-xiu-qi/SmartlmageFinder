import React from 'react';
import { Select, Button, Row, Col, Card, Tag, Spin, Empty } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { SearchImageItem } from '@/types/models';
import { VectorSearchTarget } from '@/types/search';
import RefModal from '@/components/RefModal';

const { Option } = Select;

// 定义搜索类型选项
const searchTypeOptions = [
  { value: VectorSearchTarget.IMAGE, label: '图像向量' },
  { value: VectorSearchTarget.TITLE, label: '标题向量' },
  { value: VectorSearchTarget.DESCRIPTION, label: '描述向量' },
];

interface SimilarImagesModalProps {
  open: boolean;
  onClose: () => void;
  loading: boolean;
  searchTarget: VectorSearchTarget;
  onSearchTargetChange: (value: VectorSearchTarget) => void;
  onSearch: () => void;
  similarImages: SearchImageItem[];
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
}) => {  return (
    <RefModal
      title={`相似图片 (基于${searchTypeOptions.find(opt => opt.value === searchTarget)?.label || '图像向量'})`}
      open={open}
      onCancel={onClose}
      footer={null}
      width={800}
      destroyOnClose
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

      {loading ? (
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
        <Empty description="未找到相似图片" />      )}
    </RefModal>
  );
};

export default SimilarImagesModal;
