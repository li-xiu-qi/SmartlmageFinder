import React from 'react';
import { Tag as AntTag } from 'antd';
import { Link } from 'react-router-dom';
import { TagInfo } from '@/types/models';
import '../styles.less';

interface TagCloudProps {
  tags: TagInfo[];
  searchValue?: string;
}

const TagCloud: React.FC<TagCloudProps> = ({ tags, searchValue = '' }) => {
  // 根据搜索条件过滤标签
  const filteredTags = tags.filter(tag =>
    tag.tag.toLowerCase().includes(searchValue.toLowerCase())
  );

  // 生成标签云样式
  const getTagColor = (count: number) => {
    const maxCount = Math.max(...tags.map(tag => tag.count), 1);
    const colors = ['blue', 'cyan', 'geekblue', 'purple', 'magenta', 'red', 'volcano', 'orange', 'gold', 'lime', 'green'];
    const index = Math.min(Math.floor((count / maxCount) * colors.length), colors.length - 1);
    return colors[index];
  };
  // 计算标签字体大小对应的CSS类
  const getTagSizeClass = (count: number) => {
    const maxCount = Math.max(...tags.map(tag => tag.count), 1);
    const ratio = count / maxCount;
    
    if (ratio < 0.2) return 'tag-size-xs';
    if (ratio < 0.4) return 'tag-size-sm';
    if (ratio < 0.6) return 'tag-size-md';
    if (ratio < 0.8) return 'tag-size-lg';
    if (ratio < 0.9) return 'tag-size-xl';
    return 'tag-size-xxl';
  };
  return (
    <div className="tag-cloud-container">
      {filteredTags.length > 0 ? (
        filteredTags.map(tag => (          <Link to={`/images?tags=${tag.tag}`} key={tag.tag}>            <AntTag
              color={getTagColor(tag.count)}
              className={`tag-item ${getTagSizeClass(tag.count)}`}
            >
              {tag.tag} ({tag.count})
            </AntTag>
          </Link>
        ))
      ) : (
        <div>没有匹配的标签</div>
      )}
    </div>
  );
};

export default TagCloud;
