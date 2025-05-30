import React from 'react';
import { Row, Col, Card, Empty, Image, Button, Tag, Popconfirm } from 'antd';
import { EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import ImageCard from './ImageCard';
import { ImageCardModel } from '@/utils/typeConverters';
import { ViewMode } from './ViewControls';
import dayjs from 'dayjs';

interface ImageListProps {
  images: ImageCardModel[];
  viewMode: ViewMode;
  gridColumns: number;
  onImageClick: (image: ImageCardModel) => void;
  onTagClick: (tag: string) => void;
  onDeleteImage: (id: number) => void;
  // 多选功能相关
  multiSelectMode?: boolean;
  selectedImageIds?: Set<number>;
  onImageSelect?: (imageId: number, selected: boolean) => void;
}

/**
 * 格式化日期
 */
const formatDate = (dateString: string): string => {
  return dayjs(dateString).format('YYYY-MM-DD HH:mm');
};

/**
 * 图片列表组件
 */
const ImageList: React.FC<ImageListProps> = ({
  images,
  viewMode,
  gridColumns,
  onImageClick,
  onTagClick,
  onDeleteImage,
  multiSelectMode = false,
  selectedImageIds = new Set(),
  onImageSelect
}) => {
  if (images.length === 0) {
    return <Empty description="暂无图片" />;
  }

  // 网格视图
  if (viewMode === 'grid') {
    return (
      <Row gutter={[24, 24]}>
        {images.map(image => (
          <Col
            xs={24}
            sm={12}
            md={12}
            lg={24 / gridColumns}
            xl={24 / gridColumns}
            key={image.id}
          >            <div className="image-card-wrapper">
              <ImageCard
                image={image}
                onClick={onImageClick}
                showTags={true}
                onTagClick={onTagClick}
                multiSelectMode={multiSelectMode}
                selected={selectedImageIds.has(image.id)}
                onSelect={onImageSelect}
              />
            </div>
          </Col>
        ))}
      </Row>
    );
  }

  // 列表视图
  else {
    return (
      <div className="image-list">
        {images.map(image => (
          <Card
            style={{ marginBottom: 16 }}
            key={image.id}
          >
            <div style={{ display: 'flex' }}>
              <div style={{ width: 100, height: 100, overflow: 'hidden', marginRight: 16, position: 'relative' }}>
                <Image
                  src={image.filepath}
                  alt={image.title}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  preview={{
                    mask: <div><EyeOutlined style={{ marginRight: 5 }} />预览</div>,
                  }}
                />
              </div>
              <div style={{ flex: 1 }}>
                <h3 style={{ margin: '0 0 8px' }}>{image.title}</h3>
                <p style={{ color: 'rgba(0, 0, 0, 0.45)', margin: '0 0 8px' }}>
                  上传时间: {formatDate(image.created_at)}
                </p>
                <div>
                  {image.tags.map(tag => (
                    <Tag
                      key={tag}
                      onClick={() => onTagClick(tag)}
                      style={{ cursor: 'pointer' }}
                    >
                      {tag}
                    </Tag>
                  ))}
                </div>
              </div>
              <div>
                <Button type="link" onClick={() => onImageClick(image)}>查看详情</Button>
                <Popconfirm
                  title="确定要删除这张图片吗？"
                  onConfirm={() => onDeleteImage(image.id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button type="link" danger icon={<DeleteOutlined />}>删除</Button>
                </Popconfirm>
              </div>
            </div>
          </Card>
        ))}
      </div>
    );
  }
};

export default ImageList;
