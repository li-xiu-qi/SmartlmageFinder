import React, { useState } from 'react';
import { 
  Descriptions, Image, Tag, Button, Form, Input, Select, message, Space, 
  Typography, Divider, Spin
} from 'antd';
import { EditOutlined, SaveOutlined, CloseOutlined, DeleteOutlined } from '@ant-design/icons';
import { ImageCardModel } from '@/utils/typeConverters';
import { ImageModel } from '@/types/models';
import { VectorSearchTarget } from '@/types/search';
import dayjs from 'dayjs';
import './styles.less';

const { TextArea } = Input;
const { Title } = Typography;
const { Option } = Select;

interface ImageDetailProps {
  image: ImageModel;
  onUpdate: (image: ImageModel) => void;
  onDelete: (id: number) => Promise<void>;
  onFindSimilar?: (imageId: number, searchTarget: VectorSearchTarget) => Promise<any[]>;
  onAIAnalyze?: (imageId: number) => Promise<any>;
  onUpdateTags?: (id: number, tags: string[]) => Promise<string[]>;
  loading?: boolean;
}

/**
 * 图片详情组件
 */
const ImageDetail: React.FC<ImageDetailProps> = ({
  image,
  onUpdate,
  onDelete,
  onFindSimilar,
  onAIAnalyze,
  onUpdateTags,
  loading = false
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [form] = Form.useForm();
  const [submitLoading, setSubmitLoading] = useState(false);

  const handleEditToggle = () => {
    if (isEditing) {
      setIsEditing(false);
      form.resetFields();
    } else {
      form.setFieldsValue({
        title: image.title,
        description: image.description,
        tags: image.tags,
      });
      setIsEditing(true);
    }
  };
  const handleSubmit = async () => {
    try {
      setSubmitLoading(true);
      const values = await form.validateFields();
      
      // 创建更新后的图片对象
      const updatedImage = {
        ...image,
        ...values
      };
      
      // 调用更新方法
      onUpdate(updatedImage);
      setIsEditing(false);
      message.success('更新成功');
    } catch (error) {
      console.error('表单提交错误:', error);
      message.error('更新失败，请重试');
    } finally {
      setSubmitLoading(false);
    }
  };
  const handleDelete = async () => {
    try {
      await onDelete(image.id);
    } catch (error) {
      console.error('删除失败:', error);
    }
  };

  const handleFindSimilar = async (searchTarget: VectorSearchTarget) => {
    if (onFindSimilar) {
      try {
        const results = await onFindSimilar(image.id, searchTarget);
        return results;
      } catch (error) {
        console.error('查找相似图片失败:', error);
        message.error('查找相似图片失败');
        return [];
      }
    }
    return [];
  };

  const handleAIAnalyze = async () => {
    if (onAIAnalyze) {
      try {
        setSubmitLoading(true);
        const results = await onAIAnalyze(image.id);
        
        // 更新表单数据
        if (isEditing) {
          form.setFieldsValue({
            title: results.title,
            description: results.description,
            tags: results.tags,
          });
        } else {
          // 创建更新后的图片对象
          const updatedImage = {
            ...image,
            title: results.title,
            description: results.description,
            tags: results.tags
          };
          
          // 调用更新方法
          onUpdate(updatedImage);
        }
        
        message.success('AI分析完成');
      } catch (error) {
        console.error('AI分析失败:', error);
        message.error('AI分析失败');
      } finally {
        setSubmitLoading(false);
      }
    }
  };
  // 格式化文件大小
  const formatFileSize = (bytes?: number): string => {
    if (!bytes) return '未知';
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB';
    else if (bytes < 1073741824) return (bytes / 1048576).toFixed(2) + ' MB';
    else return (bytes / 1073741824).toFixed(2) + ' GB';
  };

  return (
    <Spin spinning={loading || submitLoading}>
      <div className="image-detail">
        <div className="image-detail-header">
          <Space>
            {!isEditing ? (
              <>
                <Button icon={<EditOutlined />} onClick={handleEditToggle}>
                  编辑
                </Button>
                {onAIAnalyze && (
                  <Button onClick={handleAIAnalyze}>
                    AI分析
                  </Button>
                )}
              </>
            ) : (
              <>
                <Button icon={<SaveOutlined />} type="primary" onClick={handleSubmit}>
                  保存
                </Button>
                <Button icon={<CloseOutlined />} onClick={handleEditToggle}>
                  取消
                </Button>
                {onAIAnalyze && (
                  <Button onClick={handleAIAnalyze}>
                    AI分析填充
                  </Button>
                )}
              </>
            )}
            <Button 
              danger 
              icon={<DeleteOutlined />} 
              onClick={handleDelete}
            >
              删除
            </Button>
          </Space>
        </div>

        <div className="image-detail-preview">
          <Image 
            src={image.filepath} 
            alt={image.title}
            style={{ maxWidth: '100%', maxHeight: '400px' }}
          />
        </div>

        <Divider style={{ margin: '16px 0' }} />

        {isEditing ? (
          <Form
            form={form}
            layout="vertical"
            initialValues={{
              title: image.title,
              description: image.description,
              tags: image.tags,
            }}
          >
            <Form.Item 
              name="title" 
              label="标题"
              rules={[{ required: true, message: '请输入标题' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item 
              name="description" 
              label="描述"
            >
              <TextArea rows={4} />
            </Form.Item>
            <Form.Item 
              name="tags" 
              label="标签"
            >              <Select 
                mode="tags" 
                placeholder="添加标签"
                style={{ width: '100%' }}
              >
                {(image.tags || []).map(tag => (
                  <Option key={tag} value={tag}>{tag}</Option>
                ))}
              </Select>
            </Form.Item>
          </Form>
        ) : (
          <div className="image-detail-info">
            <Title level={4}>{image.title}</Title>
            <Descriptions column={1} layout="vertical">
              <Descriptions.Item label="上传时间">
                {dayjs(image.created_at).format('YYYY-MM-DD HH:mm:ss')}
              </Descriptions.Item>
              <Descriptions.Item label="文件路径">
                {image.filepath}
              </Descriptions.Item>
              {image.file_size !== undefined && (
                <Descriptions.Item label="文件大小">
                  {formatFileSize(image.file_size)}
                </Descriptions.Item>
              )}
              <Descriptions.Item label="描述">
                {image.description || '暂无描述'}
              </Descriptions.Item>
              <Descriptions.Item label="标签">
                {image.tags && image.tags.length > 0 ? (
                  <div>
                    {image.tags.map(tag => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </div>
                ) : (
                  '暂无标签'
                )}
              </Descriptions.Item>
            </Descriptions>
          </div>
        )}
      </div>
    </Spin>
  );
};

export default ImageDetail;
