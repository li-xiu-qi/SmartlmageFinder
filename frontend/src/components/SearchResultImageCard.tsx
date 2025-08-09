// Renamed from ImageCard.tsx to SearchResultImageCard.tsx for clarity
import React from 'react';
import { Card, Tag, Checkbox } from 'antd';
import type { CheckboxChangeEvent } from 'antd/es/checkbox';
import { ImageCardModel } from '@/utils/typeConverters';
import dayjs from 'dayjs';
import './search-result-image-card.less';

interface SearchResultImageCardProps {
  image: ImageCardModel;
  onClick?: (image: ImageCardModel) => void;
  showTags?: boolean;
  showSimilarity?: boolean;
  onTagClick?: (tag: string) => void;
  multiSelectMode?: boolean;
  selected?: boolean;
  onSelect?: (imageId: number, selected: boolean) => void;
}

const formatDate = (dateString: string): string => dayjs(dateString).format('YYYY-MM-DD HH:mm');

const processTags = (tags: unknown): string[] => {
  if (!tags) return [];
  if (typeof tags === 'string') {
    try { return JSON.parse(tags); } catch { return []; }
  }
  return Array.isArray(tags) ? tags : [];
};

const SearchResultImageCard: React.FC<SearchResultImageCardProps> = ({
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
  };

  const handleCheckboxChange = (e: CheckboxChangeEvent) => {
    e.nativeEvent?.stopPropagation();
    if (onSelect) onSelect(image.id, e.target.checked);
  };

  const handleTagClick = (e: React.MouseEvent, tag: string) => {
    e.stopPropagation();
    if (onTagClick) onTagClick(tag);
  };

  const tags = processTags(image.tags);
  return (
    <Card
      hoverable
      className={`image-card ${multiSelectMode ? 'multi-select-mode' : ''} ${selected ? 'selected' : ''}`}
      onClick={handleClick}
      cover={
        <div className="image-cover">
          <img alt={image.title} src={image.public_url || image.filepath} />
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
        <div className="image-title">{image.title}</div>
        <div className="image-meta">{formatDate(image.created_at)}</div>
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
            {tags.length > 3 && <Tag color="default" className="tag-item">+{tags.length - 3}</Tag>}
          </div>
        )}
      </div>
    </Card>
  );
};

export default SearchResultImageCard;
