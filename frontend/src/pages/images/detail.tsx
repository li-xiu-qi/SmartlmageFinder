import React, { useState } from 'react';
import { 
  Typography, 
  Descriptions, 
  Tag, 
  Button, 
  Space, 
  Input, 
  message, 
  Popconfirm,
  Form,
  Row,
  Col,
  Divider,
  Card
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  SaveOutlined,
  CloseOutlined,
  PlusOutlined,
  SearchOutlined,
  RobotOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { imageService, tagService, metadataService, aiService, searchService } from '@/services/api';
import { formatDate, formatFileSize, getImageUrl } from '@/utils/format';
import { ImageDetail } from '@/types';

const { Title, Paragraph } = Typography;

interface ImageDetailViewProps {
  image: ImageDetail;
  onUpdate: (image: ImageDetail) => void;
  onDelete: (uuid: string) => void;
}

const ImageDetailView: React.FC<ImageDetailViewProps> = ({ image, onUpdate, onDelete }) => {
  // 编辑状态管理
  const [editingTitle, setEditingTitle] = useState(false);
  const [editingDescription, setEditingDescription] = useState(false);
  const [title, setTitle] = useState(image.title);
  const [description, setDescription] = useState(image.description);
  const [newTag, setNewTag] = useState('');
  const [loading, setLoading] = useState(false);
  const [similarImages, setSimilarImages] = useState<any[]>([]);
  
  // 获取相似图片
  const fetchSimilarImages = async () => {
    try {
      setLoading(true);
      const response = await searchService.searchSimilar(image.uuid, { limit: 5 });
      if (response.status === 'success' && response.data) {
        // 过滤掉当前图片
        const filtered = response.data.results.filter(img => img.uuid !== image.uuid);
        setSimilarImages(filtered);
      }
    } catch (error) {
      console.error('获取相似图片失败:', error);
      message.error('获取相似图片失败');
    } finally {
      setLoading(false);
    }
  };

  // 更新标题
  const handleUpdateTitle = async () => {
    if (title.trim() === '') {
      message.error('标题不能为空');
      return;
    }

    try {
      setLoading(true);
      const response = await imageService.updateImage(image.uuid, { title });
      if (response.status === 'success') {
        message.success('标题更新成功');
        setEditingTitle(false);
        onUpdate({ ...image, title });
      }
    } catch (error) {
      console.error('更新标题失败:', error);
      message.error('更新标题失败');
    } finally {
      setLoading(false);
    }
  };

  // 更新描述
  const handleUpdateDescription = async () => {
    try {
      setLoading(true);
      const response = await imageService.updateImage(image.uuid, { description });
      if (response.status === 'success') {
        message.success('描述更新成功');
        setEditingDescription(false);
        onUpdate({ ...image, description });
      }
    } catch (error) {
      console.error('更新描述失败:', error);
      message.error('更新描述失败');
    } finally {
      setLoading(false);
    }
  };

  // 添加标签
  const handleAddTag = async () => {
    if (newTag.trim() === '') {
      return;
    }

    try {
      setLoading(true);
      // 检查标签是否已存在
      if (image.tags.includes(newTag)) {
        message.warning('该标签已存在');
        setNewTag('');
        return;
      }

      const response = await tagService.addTags(image.uuid, [newTag]);
      if (response.status === 'success') {
        message.success('标签添加成功');
        setNewTag('');
        onUpdate({ ...image, tags: response.data.tags });
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
      const response = await tagService.deleteTag(image.uuid, tag);
      if (response.status === 'success') {
        message.success('标签删除成功');
        onUpdate({ ...image, tags: response.data.tags });
      }
    } catch (error) {
      console.error('删除标签失败:', error);
      message.error('删除标签失败');
    } finally {
      setLoading(false);
    }
  };

  // 使用AI生成内容
  const handleGenerateContent = async () => {
    try {
      setLoading(true);
      message.loading('正在分析图片并生成内容...', 0);
      
      const response = await aiService.generateContent(image.uuid, {
        generate_title: true,
        generate_description: true,
        generate_tags: true,
        detail: 'high',
      });
      
      if (response.status === 'success' && response.data) {
        message.destroy();
        message.success('内容生成成功');
        
        const generatedData = response.data.generated;
        const updatedImage = { 
          ...image,
          title: generatedData.title || image.title,
          description: generatedData.description || image.description,
          tags: generatedData.tags || image.tags,
        };
        
        setTitle(updatedImage.title);
        setDescription(updatedImage.description);
        onUpdate(updatedImage);
      }
    } catch (error) {
      console.error('生成内容失败:', error);
      message.destroy();
      message.error('生成内容失败');
    } finally {
      setLoading(false);
    }
  };

  // 渲染元数据表格
  const renderMetadata = () => {
    const metadataEntries = Object.entries(image.metadata || {});
    if (metadataEntries.length === 0) {
      return <p>暂无元数据</p>;
    }

    return (
      <Descriptions bordered column={1} size="small">
        {metadataEntries.map(([key, value]) => (
          <Descriptions.Item key={key} label={key}>
            {value}
          </Descriptions.Item>
        ))}
      </Descriptions>
    );
  };

  return (
    <div className="image-detail-drawer">
      {/* 图片预览区域 */}
      <div className="image-preview">
        <img src={getImageUrl(image.filepath)} alt={image.title} />
      </div>

      {/* 标题和描述 */}
      <div className="detail-section">
        {editingTitle ? (
          <div style={{ display: 'flex', marginBottom: 16 }}>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              style={{ marginRight: 8 }}
            />
            <Button 
              icon={<SaveOutlined />} 
              type="primary" 
              onClick={handleUpdateTitle}
              loading={loading}
              style={{ marginRight: 8 }}
            />
            <Button 
              icon={<CloseOutlined />} 
              onClick={() => {
                setTitle(image.title);
                setEditingTitle(false);
              }} 
            />
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
            <Title level={4} style={{ margin: 0, flex: 1 }}>
              {title}
            </Title>
            <Button 
              icon={<EditOutlined />} 
              type="link" 
              onClick={() => setEditingTitle(true)}
              disabled={loading}
            />
          </div>
        )}

        {editingDescription ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
            <Input.TextArea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
            />
            <div>
              <Button 
                icon={<SaveOutlined />} 
                type="primary" 
                onClick={handleUpdateDescription}
                loading={loading}
                style={{ marginRight: 8 }}
              />
              <Button 
                icon={<CloseOutlined />} 
                onClick={() => {
                  setDescription(image.description);
                  setEditingDescription(false);
                }} 
              />
            </div>
          </div>
        ) : (
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'start' }}>
              <Paragraph style={{ flex: 1, margin: 0 }}>
                {description || '暂无描述'}
              </Paragraph>
              <Button 
                icon={<EditOutlined />} 
                type="link" 
                onClick={() => setEditingDescription(true)}
                disabled={loading}
              />
            </div>
          </div>
        )}
      </div>

      {/* 文件信息 */}
      <div className="detail-section">
        <Title level={5} className="section-title">文件信息</Title>
        <Descriptions column={2} size="small">
          <Descriptions.Item label="文件名">{image.filename}</Descriptions.Item>
          <Descriptions.Item label="文件大小">{formatFileSize(image.file_size)}</Descriptions.Item>
          <Descriptions.Item label="文件类型">{image.file_type}</Descriptions.Item>
          <Descriptions.Item label="尺寸">{`${image.width} x ${image.height}`}</Descriptions.Item>
          <Descriptions.Item label="上传时间" span={2}>{formatDate(image.created_at)}</Descriptions.Item>
        </Descriptions>
      </div>

      {/* 标签 */}
      <div className="detail-section">
        <Title level={5} className="section-title">标签</Title>
        <div style={{ marginBottom: 12 }}>
          {image.tags.map(tag => (
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
          suffix={
            <Button 
              type="text" 
              icon={<PlusOutlined />} 
              onClick={handleAddTag}
              size="small"
            />
          }
          style={{ width: 200 }}
        />
      </div>

      {/* 元数据 */}
      <div className="detail-section">
        <Title level={5} className="section-title">元数据</Title>
        {renderMetadata()}
      </div>

      {/* 操作按钮 */}
      <Divider />
      <div className="detail-actions">
        <Button
          icon={<SearchOutlined />}
          onClick={fetchSimilarImages}
          disabled={loading}
        >
          查找相似图片
        </Button>
        <Button
          icon={<RobotOutlined />}
          onClick={handleGenerateContent}
          disabled={loading}
        >
          AI分析生成
        </Button>
        <Popconfirm
          title="确定要删除这张图片吗？"
          icon={<ExclamationCircleOutlined style={{ color: 'red' }} />}
          onConfirm={() => onDelete(image.uuid)}
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

      {/* 相似图片区域 */}
      {similarImages.length > 0 && (
        <div className="detail-section" style={{ marginTop: 24 }}>
          <Title level={5} className="section-title">相似图片</Title>
          <Row gutter={[8, 8]}>
            {similarImages.map(img => (
              <Col span={8} key={img.uuid}>
                <Card
                  hoverable
                  cover={
                    <div style={{ height: 120, overflow: 'hidden' }}>
                      <img 
                        alt={img.title} 
                        src={getImageUrl(img.filepath)} 
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                      />
                    </div>
                  }
                  size="small"
                >
                  <Card.Meta
                    title={img.title}
                    description={`相似度: ${Math.round(img.score * 100)}%`}
                  />
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}
    </div>
  );
};

export default ImageDetailView;