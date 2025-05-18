import React, { useState } from 'react';
import { Button, Divider, Select, Space, Popconfirm, message } from 'antd';
import { 
  SearchOutlined, 
  RobotOutlined, 
  DeleteOutlined, 
  ExclamationCircleOutlined 
} from '@ant-design/icons';
import { aiService } from '@/services/api';
import { ImageDetail } from '@/types';
import { AnalysisDetailLevel } from '@/types/ai';

const { Option } = Select;

// 定义搜索类型选项
const searchTypeOptions = [
  { value: 'image', label: '图像向量' },
  { value: 'title', label: '标题向量' },
  { value: 'description', label: '描述向量' },
];

interface ActionsPanelProps {
  image: ImageDetail;
  searchType: string;
  onSearchTypeChange: (value: string) => void;
  onFindSimilar: () => void;
  onDelete: (id: number) => void;
  onUpdate: (image: ImageDetail) => void;
  loading: boolean;
}

/**
 * 操作面板组件
 */
const ActionsPanel: React.FC<ActionsPanelProps> = ({
  image,
  searchType,
  onSearchTypeChange,
  onFindSimilar,
  onDelete,
  onUpdate,
  loading
}) => {
  // 使用AI生成内容
  const handleGenerateContent = async () => {
    try {
      message.loading('正在分析图片并生成内容...', 0);
      
      const response = await aiService.analyzeExistingImage(image.id, {
        detail: AnalysisDetailLevel.HIGH,
      });
      
      if (response.status === 'success' && response.data) {
        message.destroy();
        message.success('内容生成成功');
        
        const updatedImage = { 
          ...image,
          title: response.data.title || image.title,
          description: response.data.description || image.description,
          tags: response.data.tags || image.tags,
        };
        
        onUpdate(updatedImage);
      }
    } catch (error) {
      console.error('生成内容失败:', error);
      message.destroy();
      message.error('生成内容失败');
    }
  };

  return (
    <>
      <Divider />
      <div className="detail-actions">
        <Space>
          <Select
            value={searchType}
            onChange={onSearchTypeChange}
            style={{ width: 110 }}
          >
            {searchTypeOptions.map(option => (
              <Option key={option.value} value={option.value}>{option.label}</Option>
            ))}
          </Select>
          <Button
            icon={<SearchOutlined />}
            onClick={onFindSimilar}
            disabled={loading}
          >
            查找相似图片
          </Button>
        </Space>
        <Button
          icon={<RobotOutlined />}
          onClick={handleGenerateContent}
          disabled={loading}
        >
          AI分析生成
        </Button>
        <Popconfirm          title="确定要删除这张图片吗？"
          icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
          onConfirm={() => onDelete(image.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button
            danger
            icon={<DeleteOutlined />}
            disabled={loading}
          >
            删除图片
          </Button>
        </Popconfirm>
      </div>
    </>
  );
};

export default ActionsPanel;
