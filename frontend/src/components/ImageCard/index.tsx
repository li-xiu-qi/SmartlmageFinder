import React from 'react';
import { Card, Tag } from 'antd';
import { Image, ImageSearchResult } from '@/types';
import { formatDate, getImageUrl } from '@/utils/format';

interface ImageCardProps {
  image: Image | ImageSearchResult;
  onClick?: (image: Image | ImageSearchResult) => void;
  showTags?: boolean;
  showSimilarity?: boolean;
  onTagClick?: (tag: string) => void;
}

// 处理标签数据，确保为数组格式
const processTags = (tags: any): string[] => {
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
  onTagClick
}) => {
  const isSearchResult = 'score' in image;
  
  const handleClick = () => {
    if (onClick) {
      onClick(image);
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

  return (
    <Card
      hoverable
      className="image-card"
      onClick={handleClick}
      cover={
        <div className="image-cover" style={{ 
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          backgroundColor: '#f0f0f0',
          overflow: 'hidden',
          maxHeight: '400px'
        }}>
          <img 
            alt={image.title} 
            src={getImageUrl(image.filepath)} 
            style={{ 
              width: '100%',
              maxHeight: '400px',
              objectFit: 'contain'
            }}
          />
          {isSearchResult && showSimilarity && (
            <div className="similarity-indicator">
              {`相似度: ${Math.round((image as ImageSearchResult).score * 100)}%`}
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
                style={{ 
                  marginRight: 4, 
                  marginBottom: 4, 
                  fontSize: '12px', 
                  padding: '0 5px',
                  cursor: 'pointer'
                }}
              >
                {tag}
              </Tag>
            ))}
            {tags.length > 3 && (
              <Tag color="default" style={{ fontSize: '12px', padding: '0 5px' }}>+{tags.length - 3}</Tag>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};

export default ImageCard;