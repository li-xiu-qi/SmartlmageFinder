import React from 'react';
// 导入 Ant Design 的 UploadProps 类型
import { UploadProps } from 'antd';
// 导入自定义的 UploadFile 类型
import { UploadFile } from '../types';
// 导入增强的复制粘贴上传组件
import EnhancedUploadDropzone from '@/components/EnhancedUploadDropzone';

// 定义 UploadDropzone 组件的 props 类型接口
interface UploadDropzoneProps {
  fileList: UploadFile[]; // 当前文件列表
  onChange: UploadProps['onChange']; // 文件状态改变时的回调函数 (来自 antd)
  onRemove: (file: UploadFile) => boolean | Promise<boolean>; // 移除文件时的回调函数
  disabled?: boolean; // 是否禁用上传区域
}

// UploadDropzone 组件：封装了增强的拖拽上传组件，支持复制粘贴功能
// 注意：此组件只负责文件选择、拖拽上传和复制粘贴功能，不显示文件列表
// 文件列表的显示由单独的 FileListView 组件负责
const UploadDropzone: React.FC<UploadDropzoneProps> = ({ fileList, onChange, onRemove, disabled }) => {
  return (
    <EnhancedUploadDropzone
      fileList={fileList}
      onChange={onChange}
      onRemove={onRemove}
      disabled={disabled}
      accept="image/*"
      maxSize={10}
      multiple={true}
    />
  );
};

export default UploadDropzone;
