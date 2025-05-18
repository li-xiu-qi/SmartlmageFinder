import React from 'react';
import { Form, Input, Select, FormInstance } from 'antd';
import { UploadFile, ImageMetadata, SelectableTag } from '../types';
import RefModal from '@/components/RefModal';

// 自动调整大小的文本域
const { TextArea } = Input;

interface MetadataModalProps {
  visible: boolean; // 控制模态框是否可见
  currentFile: UploadFile | null; // 当前正在编辑的文件
  form: FormInstance; // 表单实例，用于外部控制
  availableTags: SelectableTag[]; // 可用标签列表
  onSave: () => void; // 保存回调
  onCancel: () => void; // 取消回调
}

/**
 * 图片元数据编辑模态框
 * 用于编辑单个图片的元数据，包括标题、描述、标签等
 */
const MetadataModal: React.FC<MetadataModalProps> = ({
  visible,
  currentFile,
  form,
  availableTags,
  onSave,
  onCancel
}) => {
  // 渲染模态框标题
  const renderTitle = () => {
    return currentFile 
      ? `编辑图片 "${currentFile.name}" 的元数据` 
      : '编辑图片元数据';
  };
  return (
    <RefModal
      title={renderTitle()}
      open={visible}
      onOk={onSave}
      onCancel={onCancel}
      okText="保存"
      cancelText="取消"
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{}} // 初始值在父组件中设置
      >
        {/* 图片标题 */}
        <Form.Item
          name="title"
          label="图片标题"
          rules={[{ required: true, message: '请输入图片标题' }]}
        >
          <Input placeholder="输入图片标题" />
        </Form.Item>

        {/* 图片描述 */}
        <Form.Item
          name="description"
          label="图片描述"
        >
          <TextArea 
            rows={4} 
            placeholder="输入图片描述内容" 
          />
        </Form.Item>

        {/* 图片标签 */}
        <Form.Item
          name="tags"
          label="图片标签"
        >
          <Select
            mode="tags"
            style={{ width: '100%' }}
            placeholder="输入或选择标签"
            options={availableTags}
          />
        </Form.Item>

        {/* 地点信息（可选） */}
        <Form.Item
          name="location"
          label="拍摄地点"
        >
          <Input placeholder="输入拍摄地点（可选）" />
        </Form.Item>

        {/* 事件信息（可选） */}
        <Form.Item
          name="event"
          label="相关事件"
        >
          <Input placeholder="输入相关事件（可选）" />
        </Form.Item>      </Form>
    </RefModal>
  );
};

export default MetadataModal;
