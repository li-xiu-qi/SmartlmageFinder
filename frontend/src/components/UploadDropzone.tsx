import React, { useEffect, useRef } from 'react';
import { Upload, message, Card, Typography, Space, Row, Col } from 'antd';
import { InboxOutlined, CopyOutlined, CloudUploadOutlined } from '@ant-design/icons';
import type { UploadProps, UploadFile, RcFile } from 'antd/es/upload';

const { Dragger } = Upload;
const { Text } = Typography;

interface UploadDropzoneProps {
  fileList: UploadFile[];
  onChange: UploadProps['onChange'];
  onRemove: (file: UploadFile) => boolean | Promise<boolean>;
  disabled?: boolean;
  accept?: string;
  maxSize?: number; // MB
  multiple?: boolean;
  onPasteUpload?: (file: File) => void; // 复制粘贴上传回调
  showPasteArea?: boolean; // 是否显示粘贴区域
}

/**
 * 统一的上传组件，支持拖拽、点击选择和复制粘贴功能
 */
const UploadDropzone: React.FC<UploadDropzoneProps> = ({
  fileList,
  onChange,
  onRemove,
  disabled,
  accept = 'image/*',
  maxSize = 10,
  multiple = true,
  onPasteUpload,
  showPasteArea = true
}) => {
  const pasteAreaRef = useRef<HTMLDivElement>(null);

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
    if (disabled) return;

    const items = event.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      
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

  // 设置粘贴事件监听器
  useEffect(() => {
    const pasteArea = pasteAreaRef.current;
    if (pasteArea && showPasteArea) {
      pasteArea.addEventListener('paste', handlePaste);
      return () => {
        pasteArea.removeEventListener('paste', handlePaste);
      };
    }
  }, [disabled, fileList, onPasteUpload, showPasteArea]);

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
    <div>
      <Row gutter={[16, 16]}>
        {/* 粘贴区域 */}
        {showPasteArea && (
          <Col span={24}>
            <Card
              size="small"
              style={{
                border: '2px dashed #1890ff',
                backgroundColor: '#f6ffed',
                cursor: 'text'
              }}
            >
              <div
                ref={pasteAreaRef}
                tabIndex={0}
                style={{
                  padding: '12px',
                  textAlign: 'center',
                  outline: 'none',
                  minHeight: '60px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
                onClick={() => {
                  pasteAreaRef.current?.focus();
                }}
              >
                <Space direction="vertical" size="small">
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <CopyOutlined style={{ color: '#52c41a', fontSize: 16 }} />
                    <Text strong style={{ color: '#52c41a' }}>
                      点击此区域，然后按 Ctrl+V 粘贴剪贴板中的图片
                    </Text>
                  </div>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    支持从网页、截图工具、图片编辑器等复制的图片
                  </Text>
                </Space>
              </div>
            </Card>
          </Col>
        )}

        {/* 上传区域 */}
        <Col span={24}>
          <Dragger {...uploadProps}>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">
              <CloudUploadOutlined /> 点击或拖拽文件到此区域进行上传
            </p>
            <p className="ant-upload-hint">
              支持{multiple ? '单个或批量' : '单个'}上传。只允许 JPG/PNG/GIF/WEBP 格式，最大 {maxSize}MB。
            </p>
          </Dragger>
        </Col>
      </Row>
    </div>
  );
};

export default UploadDropzone;
