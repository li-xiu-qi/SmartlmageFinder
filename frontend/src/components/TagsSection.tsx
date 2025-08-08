import React, { useState } from 'react';
import { Tag, Input, Button, Typography, message, Modal, Space } from 'antd';
import { PlusOutlined, EditOutlined } from '@ant-design/icons';
import { tagService } from '@/services/api';

const { Title } = Typography;

interface TagsSectionProps {
  imageId: number;
  tags: string[] | undefined;
  onTagsUpdate: (tags: string[]) => void;
}

/**
 * 标签管理组件
 */
const TagsSection: React.FC<TagsSectionProps> = ({ imageId, tags, onTagsUpdate }) => {
  const [newTag, setNewTag] = useState('');
  const [loading, setLoading] = useState(false);
  const [isEditModalVisible, setIsEditModalVisible] = useState(false);
  const [editableTags, setEditableTags] = useState<string[]>([]);

  // 打开批量编辑标签模态框
  const showEditTagsModal = () => {
    setEditableTags([...(tags || [])]);
    setIsEditModalVisible(true);
  };

  // 关闭批量编辑标签模态框
  const handleCancelEditTags = () => {
    setIsEditModalVisible(false);
  };

  // 保存批量编辑的标签
  const handleSaveEditTags = async () => {
    try {
      setLoading(true);
      // 使用更新标签的API（覆盖方式）
      const response = await tagService.updateImageTags(imageId, editableTags);
      if (response.status === 'success') {
        message.success('标签更新成功');
        onTagsUpdate(response.data.tags);
        setIsEditModalVisible(false);
      }
    } catch (error) {
      console.error('更新标签失败:', error);
      message.error('更新标签失败');
    } finally {
      setLoading(false);
    }
  };

  // 在批量编辑模式下添加新标签
  const handleAddEditableTag = (tag: string) => {
    if (!tag.trim()) return;
    
    // 检查是否已存在
    if (editableTags.includes(tag)) {
      message.warning('该标签已存在');
      return;
    }
    
    setEditableTags([...editableTags, tag]);
  };

  // 在批量编辑模式下移除标签
  const handleRemoveEditableTag = (tagToRemove: string) => {
    setEditableTags(editableTags.filter(tag => tag !== tagToRemove));
  };



  return (
    <div className="detail-section">
      <Title level={5} className="section-title">标签</Title>
      <div style={{ marginBottom: 12 }}>
        {(tags || []).map(tag => (
          <Tag
            key={tag}
            style={{ marginBottom: 8 }}
          >
            {tag}
          </Tag>
        ))}
      </div>
      
      <Button
        type="primary"
        icon={<EditOutlined />}
        onClick={showEditTagsModal}
        loading={loading}
        style={{ marginTop: 16 }}
      >
        批量编辑标签
      </Button>      <Modal
        title="批量编辑标签"
        open={isEditModalVisible}
        onOk={handleSaveEditTags}
        onCancel={handleCancelEditTags}
        confirmLoading={loading}
      >        <div>
          <div style={{ marginBottom: 16 }}>
            <Typography.Text style={{ marginBottom: 8, display: 'block' }}>
              当前标签列表：
            </Typography.Text>
            <div style={{ marginBottom: 12 }}>
              {editableTags.map(tag => (
                <Tag
                  key={tag}
                  closable
                  onClose={() => handleRemoveEditableTag(tag)}
                  style={{ marginBottom: 8 }}
                >
                  {tag}
                </Tag>
              ))}
              {editableTags.length === 0 && (
                <Typography.Text type="secondary">暂无标签，请在下方添加</Typography.Text>
              )}
            </div>
          </div>
          
          <div style={{ marginTop: 16 }}>
            <Typography.Text style={{ marginBottom: 8, display: 'block' }}>
              添加新标签：
            </Typography.Text>
            <Space.Compact style={{ width: '100%' }}>
              <Input
                placeholder="输入新标签名称"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onPressEnter={() => {
                  handleAddEditableTag(newTag);
                  setNewTag(''); // 清空输入框
                }}
                disabled={loading}
              />
              <Button 
                type="primary" 
                icon={<PlusOutlined />} 
                onClick={() => {
                  handleAddEditableTag(newTag);
                  setNewTag(''); // 清空输入框
                }}
                loading={loading}
              >
                添加
              </Button>
            </Space.Compact>
          </div>
          
          {/* 提示信息 */}
          <Typography.Text type="secondary" style={{ marginTop: 16, display: 'block' }}>
            提示：点击标签旁边的"×"可删除标签，点击"确定"保存所有更改
          </Typography.Text>
        </div>
      </Modal>
    </div>
  );
};

export default TagsSection;
