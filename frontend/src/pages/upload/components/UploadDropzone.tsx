import React from 'react';
// 导入 Ant Design 图标
import { InboxOutlined } from '@ant-design/icons';
// 导入 Ant Design 的 Upload 组件、UploadProps 类型和 message 组件
import { Upload, UploadProps, message } from 'antd';
// 导入自定义的 UploadFile 类型
import { UploadFile } from '../types';

// 从 Upload 组件中解构出 Dragger 组件，用于拖拽上传
const { Dragger } = Upload;

// 定义 UploadDropzone 组件的 props 类型接口
interface UploadDropzoneProps {
  fileList: UploadFile[]; // 当前文件列表
  onChange: UploadProps['onChange']; // 文件状态改变时的回调函数 (来自 antd)
  onRemove: (file: UploadFile) => boolean | Promise<boolean>; // 移除文件时的回调函数
  disabled?: boolean; // 是否禁用上传区域
}

// UploadDropzone 组件：封装了 Ant Design 的 Dragger 组件，用于文件拖拽上传
const UploadDropzone: React.FC<UploadDropzoneProps> = ({ fileList, onChange, onRemove, disabled }) => {
  // 配置 Ant Design Upload 组件的 props
  const props: UploadProps = {
    name: 'file', // 后端接收文件的字段名 (如果直接通过 Upload 组件上传)
    multiple: true, // 是否支持多文件选择
    fileList: fileList, // 受控：当前已选择的文件列表
    onChange: onChange, // 文件状态改变时的回调 (如添加、上传中、成功、失败)
    onRemove: onRemove as any, // 移除文件时的回调 (类型断言 as any 是因为我们自定义的 UploadFile 与 antd 的可能存在细微差异，但功能兼容)
    beforeUpload: (file) => { // 上传文件之前的钩子，用于校验文件或阻止自动上传
      // 校验文件类型：只允许 JPG/PNG/GIF/WEBP 格式
      const isJpgOrPngOrGifOrWebp = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/gif' || file.type === 'image/webp';
      if (!isJpgOrPngOrGifOrWebp) {
        message.error('只能上传 JPG/PNG/GIF/WEBP 格式的图片!');
      }
      // 校验文件大小：不能超过 10MB
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('图片大小必须小于 10MB!');
      }
      // 如果任一校验失败，则阻止文件被添加到列表（如果 onChange 中不处理）或自动上传
      // 在这个应用中，我们手动管理上传过程，所以 beforeUpload 主要用于校验。
      // 返回 false 会阻止 antd 的默认上传行为，文件仍会通过 onChange 回调添加到 fileList 中，由我们控制后续操作。
      return false; 
    },
    disabled: disabled, // 控制整个拖拽区域是否可用
  };

  return (
    // 使用 Dragger 组件实现拖拽上传区域
    <Dragger {...props}>
      <p className="ant-upload-drag-icon">
        <InboxOutlined /> {/* 上传图标 */}
      </p>
      <p className="ant-upload-text">点击或拖拽文件到此区域进行上传</p>
      <p className="ant-upload-hint">
        支持单个或批量上传。请勿上传公司内部资料及其他敏感或违规文件。
      </p>
    </Dragger>
  );
};

export default UploadDropzone;
