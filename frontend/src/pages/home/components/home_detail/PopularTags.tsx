import React from 'react';
import { Tag, Empty, Tooltip } from 'antd';
import { Link } from 'react-router-dom';
import { PopularTagsProps } from '../../types';
import './styles.less';

/**
 * 热门标签组件
 * 展示系统中使用频率最高的标签
 */
const PopularTags: React.FC<PopularTagsProps> = ({ tags }) => {
  // 获取颜色，基于标签使用频率
  const getTagColor = (count: number): string => {
    if (tags.length === 0) return 'blue';
    
    const maxCount = Math.max(...tags.map(tag => tag.count));
    const minCount = Math.min(...tags.map(tag => tag.count));
    
    const colors = ['blue', 'cyan', 'geekblue', 'gold', 'green', 'lime', 'magenta', 'orange', 'purple', 'red', 'volcano'];
    
    if (maxCount === minCount) return colors[Math.floor(Math.random() * colors.length)];
    
    const index = Math.floor(((count - minCount) / (maxCount - minCount)) * (colors.length - 1));
    return colors[index];
  };

  return (
    <div className="hot-tags">
      <h2 className="section-title">热门标签</h2>
      {tags.length > 0 ? (
        <div className="tags-container">
          {tags.map(tag => (
            <Tooltip title={`${tag.count} 张图片使用此标签`} key={tag.tag}>
              <Link to={`/images?tags=${tag.tag}`}>
                <Tag 
                  color={getTagColor(tag.count)} 
                  className="tag-item"
                >
                  {tag.tag} ({tag.count})
                </Tag>
              </Link>
            </Tooltip>
          ))}
        </div>
      ) : (
        <Empty description="暂无标签" />
      )}
    </div>
  );
};

export default PopularTags;
