import React, { useState } from 'react';
import { Tag, Input, Button, Typography, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { tagService } from '@/services/api';

const { Title } = Typography;

interface TagsSectionProps {
  uuid: string;
  tags: string[];
  onTagsUpdate: (tags: string[]) => void;
}

/**
 * 标签管理组件
 */
const TagsSection: React.FC<TagsSectionProps> = ({ uuid, tags, onTagsUpdate }) => {
  const [newTag, setNewTag] = useState('');
  const [loading, setLoading] = useState(false);

  // 添加标签
  const handleAddTag = async () => {
    if (newTag.trim() === '') {
      return;
    }

    try {
      setLoading(true);
      // 检查标签是否已存在
      if (tags.includes(newTag)) {
        message.warning('该标签已存在');
        setNewTag('');
        return;
      }

      const response = await tagService.addTags(uuid, [newTag]);
      if (response.status === 'success') {
        message.success('标签添加成功');
        setNewTag('');
        onTagsUpdate(response.data.tags);
      }
    } catch (error) {
      console.error('添加标签失败:', error);
      message.error('添加标签失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除标签
  const handleDeleteTag = async (tag: string) => {
    try {
      setLoading(true);
      const response = await tagService.deleteTag(uuid, tag);
      if (response.status === 'success') {
        message.success('标签删除成功');
        onTagsUpdate(response.data.tags);
      }
    } catch (error) {
      console.error('删除标签失败:', error);
      message.error('删除标签失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="detail-section">
      <Title level={5} className="section-title">标签</Title>
      <div style={{ marginBottom: 12 }}>
        {tags.map(tag => (
          <Tag
            key={tag}
            closable
            onClose={() => handleDeleteTag(tag)}
            style={{ marginBottom: 8 }}
          >
            {tag}
          </Tag>
        ))}
      </div>
      <Input
        placeholder="添加新标签"
        value={newTag}
        onChange={(e) => setNewTag(e.target.value)}
        onPressEnter={handleAddTag}
        disabled={loading}
        suffix={
          <Button 
            type="text" 
            icon={<PlusOutlined />} 
            onClick={handleAddTag}
            size="small"
            disabled={loading}
          />
        }
        style={{ width: 200 }}
      />
    </div>
  );
};

export default TagsSection;
