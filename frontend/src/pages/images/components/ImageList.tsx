import React from 'react';
import { Card, Empty, Image, Button, Tag, Popconfirm, Checkbox } from 'antd';
import { EyeOutlined, DeleteOutlined } from '@ant-design/icons';
import type { CheckboxChangeEvent } from 'antd/es/checkbox';
import GalleryImageCard from '@/components/GalleryImageCard';
import { ImageCardModel } from '@/utils/typeConverters';
import { ViewMode } from './ViewControls';
import dayjs from 'dayjs';
import { getImageUrl } from '@/utils/typeConverters';

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

// 处理标签数据，确保为数组格式
const processTags = (tags: unknown): string[] => {
  if (!tags) return [];

  // 如果是字符串，尝试解析JSON
  if (typeof tags === 'string') {
    try {
      return JSON.parse(tags);
    } catch (e) {
      // 如果解析失败，返回空数组
      console.error('标签解析失败:', e);
      return [];
    }
  }

  // 确保返回的是数组
  return Array.isArray(tags) ? tags : [];
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

  // 网格视图（画廊）
  if (viewMode === 'grid') {
    const colClass: Record<number, string> = {
      2: 'grid-cols-1 sm:grid-cols-2',
      3: 'grid-cols-2 sm:grid-cols-3',
      4: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4',
      5: 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5',
      6: 'grid-cols-2 sm:grid-cols-4 lg:grid-cols-6',
    };
    return (
      <div className={`grid gap-4 ${colClass[gridColumns] || colClass[4]}`}>
        {images.map((image) => (
          <GalleryImageCard
            key={image.id}
            image={image}
            onClick={onImageClick}
            showTags
            onTagClick={onTagClick}
            multiSelectMode={multiSelectMode}
            selected={selectedImageIds.has(image.id)}
            onSelect={onImageSelect}
          />
        ))}
      </div>
    );
  }

  // 列表视图
  else {
    // 处理列表项点击
    const handleListItemClick = (image: ImageCardModel) => {
      if (multiSelectMode && onImageSelect) {
        onImageSelect(image.id, !selectedImageIds.has(image.id));
      } else {
        onImageClick(image);
      }
    };

    // 处理复选框变化
    const handleCheckboxChange = (e: CheckboxChangeEvent, imageId: number) => {
      e.nativeEvent?.stopPropagation();
      if (onImageSelect) {
        onImageSelect(imageId, e.target.checked);
      }
    };

    // 处理标签点击
    const handleTagClick = (e: React.MouseEvent, tag: string) => {
      e.stopPropagation(); // 阻止事件冒泡
      onTagClick(tag);
    };

    return (
      <div className="image-list">
        {images.map(image => {
          const tags = processTags(image.tags);
          const isSelected = selectedImageIds.has(image.id);

          return (
            <Card
              style={{ marginBottom: 16 }}
              key={image.id}
              className={`${multiSelectMode ? 'multi-select-mode' : ''} ${isSelected ? 'selected' : ''}`}
              onClick={() => handleListItemClick(image)}
            >
              <div style={{ display: 'flex' }}>
                {/* 多选模式下的复选框 */}
                {multiSelectMode && (
                  <div style={{ marginRight: 16, display: 'flex', alignItems: 'center' }}>
                    <Checkbox
                      checked={isSelected}
                      onChange={(e) => handleCheckboxChange(e, image.id)}
                    />
                  </div>
                )}

                <div style={{ width: 100, height: 100, overflow: 'hidden', marginRight: 16, position: 'relative' }}>
                  <Image
                    src={getImageUrl(image as any)}
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
                    {tags.map(tag => (
                      <Tag
                        key={tag}
                        onClick={(e) => handleTagClick(e, tag)}
                        style={{ cursor: 'pointer' }}
                      >
                        {tag}
                      </Tag>
                    ))}
                  </div>
                </div>

                {/* 操作按钮区域 - 在多选模式下隐藏，避免混淆 */}
                {!multiSelectMode && (
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
                )}
              </div>
            </Card>
          );
        })}
      </div>
    );
  }
};

export default ImageList;
