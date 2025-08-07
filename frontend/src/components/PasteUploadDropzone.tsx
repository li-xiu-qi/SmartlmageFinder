import React, { useEffect, useRef } from 'react';
import { Upload, message, Space } from 'antd';
import { InboxOutlined, CopyOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile, RcFile } from 'antd/es/upload';

const { Dragger } = Upload;

interface PasteUploadDropzoneProps {
  fileList: UploadFile[];
  onChange: UploadProps['onChange'];
  onRemove: (file: UploadFile) => boolean | Promise<boolean>;
  disabled?: boolean;
  accept?: string;
  maxSize?: number; // MB
  multiple?: boolean;
  onPasteUpload?: (file: File) => void; // 复制粘贴上传回调
}

/**
 * 支持复制粘贴的增强上传组件
 * 在原有拖拽上传基础上增加了从剪贴板粘贴图片的功能
 */
const PasteUploadDropzone: React.FC<PasteUploadDropzoneProps> = ({
  fileList,
  onChange,
  onRemove,
  disabled,
  accept = 'image/*',
  maxSize = 10,
  multiple = true,
  onPasteUpload
}) => {
  const dropzoneRef = useRef<HTMLDivElement>(null);

  // 验证文件类型和大小
  const validateFile = (file: File): { valid: boolean; message?: string } => {
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        message: '只能上传 JPG/PNG/GIF/WEBP 格式的图片!'
      };
    }

    // 验证文件大小
    const isLtMaxSize = file.size / 1024 / 1024 < maxSize;
    if (!isLtMaxSize) {
      return {
        valid: false,
        message: `图片大小必须小于 ${maxSize}MB!`
      };
    }

    return { valid: true };
  };

  // 处理剪贴板粘贴事件
  const handlePaste = async (event: ClipboardEvent) => {
    // 检查是否禁用
    if (disabled) return;

    const items = event.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      
      // 检查是否为图片类型
      if (item.type.indexOf('image') !== -1) {
        const file = item.getAsFile();
        if (file) {
          const validation = validateFile(file);
          if (!validation.valid) {
            message.error(validation.message);
            return;
          }

          // 创建新的文件名（基于时间戳）
          const timestamp = new Date().getTime();
          const extension = file.type.split('/')[1];
          const newFile = new File([file], `pasted-image-${timestamp}.${extension}`, {
            type: file.type
          });

          // 如果有粘贴回调，调用它
          if (onPasteUpload) {
            onPasteUpload(newFile);
          } else {
            // 否则创建 UploadFile 对象并触发 onChange
            const uploadFile: UploadFile = {
              uid: `paste-${timestamp}`,
              name: newFile.name,
              status: 'done',
              size: newFile.size,
              type: newFile.type,
              originFileObj: newFile as RcFile
            };

            // 模拟上传事件
            if (onChange) {
              onChange({
                file: uploadFile,
                fileList: [...fileList, uploadFile]
              });
            }
          }

          message.success('图片已从剪贴板添加！');
          event.preventDefault();
          break;
        }
      }
    }
  };

  // 处理键盘快捷键
  const handleKeyDown = (event: KeyboardEvent) => {
    // Ctrl+V 或 Cmd+V
    if ((event.ctrlKey || event.metaKey) && event.key === 'v') {
      // 检查焦点是否在上传区域内
      if (dropzoneRef.current?.contains(document.activeElement)) {
        event.preventDefault();
        // 这里我们不能直接处理粘贴，因为需要实际的 paste 事件来获取剪贴板数据
        message.info('请使用 Ctrl+V 直接粘贴图片');
      }
    }
  };

  // 设置事件监听器
  useEffect(() => {
    const handleGlobalPaste = (event: ClipboardEvent) => {
      // 检查是否是在粘贴区域内触发的
      const target = event.target as HTMLElement;
      if (dropzoneRef.current?.contains(target)) {
        handlePaste(event);
      }
    };

    document.addEventListener('paste', handleGlobalPaste);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('paste', handleGlobalPaste);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [disabled, fileList, onPasteUpload]);

  // 上传组件配置
  const uploadProps: UploadProps = {
    name: 'file',
    multiple,
    fileList,
    onChange,
    onRemove: onRemove as any,
    showUploadList: false,
    beforeUpload: (file) => {
      const validation = validateFile(file);
      if (!validation.valid) {
        message.error(validation.message);
        return false;
      }
      return false;
    },
    disabled,
    accept
  };

  return (
    <div
      ref={dropzoneRef}
      style={{ outline: 'none' }}
    >
      {/* 粘贴提示区域 */}
      <div style={{ 
        marginBottom: 16, 
        padding: 12, 
        border: '1px dashed #1890ff', 
        borderRadius: 6,
        background: '#f0f8ff',
        textAlign: 'center',
        cursor: 'text'
      }}
      onClick={(e) => {
        e.stopPropagation();
        (e.target as HTMLElement).focus();
      }}
      tabIndex={0}
      >
        <Space direction="vertical" size="small">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            <CopyOutlined style={{ color: '#1890ff' }} />
            <span style={{ color: '#1890ff', fontWeight: 500 }}>
              点击此区域，然后按 Ctrl+V 粘贴剪贴板中的图片
            </span>
          </div>
        </Space>
      </div>

      {/* 原有的拖拽上传区域 */}
      <Dragger {...uploadProps}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域进行上传</p>
        <p className="ant-upload-hint">
          支持单个或批量上传。只允许 JPG/PNG/GIF/WEBP 格式。
        </p>
      </Dragger>
    </div>
  );
};

export default PasteUploadDropzone;
