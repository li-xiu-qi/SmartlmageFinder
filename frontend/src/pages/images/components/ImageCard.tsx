import React from 'react';
import { Card, Tag, Checkbox } from 'antd';
import type { CheckboxChangeEvent } from 'antd/es/checkbox';
import { ImageCardModel } from '@/utils/typeConverters';
import dayjs from 'dayjs';
import '../styles/components.less';

interface ImageCardProps {
  image: ImageCardModel;
  onClick?: (image: ImageCardModel) => void;
  showTags?: boolean;
  showSimilarity?: boolean;
  onTagClick?: (tag: string) => void;
  // 多选功能相关
  multiSelectMode?: boolean;
  selected?: boolean;
  onSelect?: (imageId: number, selected: boolean) => void;
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

const ImageCard: React.FC<ImageCardProps> = ({
  image,
  onClick,
  showTags = false,
  showSimilarity = false,
  onTagClick,
  multiSelectMode = false,
  selected = false,
  onSelect
}) => {
  const isSearchResult = typeof image.score !== 'undefined';

  const handleClick = () => {
    if (multiSelectMode && onSelect) {
      onSelect(image.id, !selected);
    } else if (onClick) {
      onClick(image);
    }
  };  const handleCheckboxChange = (e: CheckboxChangeEvent) => {
    e.nativeEvent?.stopPropagation();
    if (onSelect) {
      onSelect(image.id, e.target.checked);
    }
  };

  // 处理标签点击
  const handleTagClick = (e: React.MouseEvent, tag: string) => {
    e.stopPropagation(); // 阻止事件冒泡，避免触发卡片点击
    if (onTagClick) {
      onTagClick(tag);
    }
  };

  // 处理图片标签
  const tags = processTags(image.tags);
  // 统一使用后端提供的 public_url (优先)；兼容旧数据回退到 filepath
  return (
    <Card
      hoverable
      className={`image-card ${multiSelectMode ? 'multi-select-mode' : ''} ${selected ? 'selected' : ''}`}
      onClick={handleClick}cover={
        <div className="image-cover">
          <img
            alt={image.title}
            src={image.public_url || image.filepath}
          />
          {multiSelectMode && (
            <div className="selection-overlay">
              <Checkbox
                checked={selected}
                onChange={handleCheckboxChange}
                className="selection-checkbox"
              />
            </div>
          )}
          {isSearchResult && showSimilarity && (
            <div className="similarity-indicator">
              {`相似度: ${Math.round((image.score || 0) * 100)}%`}
            </div>
          )}
        </div>
      }
      styles={{ body: { padding: '16px', height: 'auto', minHeight: '120px' } }}
    >
      <div className="image-info">
        <div className="image-title">
          {image.title}
        </div>
        <div className="image-meta">
          {formatDate(image.created_at)}
        </div>
        {showTags && tags.length > 0 && (
          <div className="image-tags">
            {tags.slice(0, 3).map(tag => (
              <Tag
                key={tag}
                color="blue"
                onClick={(e) => handleTagClick(e, tag)}
                className="tag-item"
              >
                {tag}
              </Tag>
            ))}
            {tags.length > 3 && (
              <Tag color="default" className="tag-item">+{tags.length - 3}</Tag>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};

export default ImageCard;
