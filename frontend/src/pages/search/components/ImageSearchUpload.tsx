import React, { useState } from 'react';
import { Button, Space } from 'antd';
import { DeleteOutlined, CopyOutlined, FileImageOutlined } from '@ant-design/icons';
import type { RcFile, UploadFile } from 'antd/es/upload';
import UploadDropzone from '@/components/UploadDropzone';

interface ImageSearchUploadProps {
  fileList: UploadFile[];
  onFileChange: (file: RcFile | null) => void;
  onImageUrlChange: (url: string) => void;
  maxSize?: number;
  disabled?: boolean;
  imageUrl?: string;
}

/**
 * 图片搜索专用的上传组件
 * 支持拖拽、点击选择和复制粘贴
 */
const ImageSearchUpload: React.FC<ImageSearchUploadProps> = ({
  fileList,
  onFileChange,
  onImageUrlChange,
  maxSize = 10,
  disabled = false,
  imageUrl
}) => {
  const [localFileList, setLocalFileList] = useState<UploadFile[]>(fileList);

  // 处理文件粘贴
  const handlePasteUpload = (file: File) => {
    const rcFile = file as RcFile;
    
    // 设置文件
    onFileChange(rcFile);
    
    // 创建预览URL
    const previewUrl = URL.createObjectURL(file);
    onImageUrlChange(previewUrl);
    
    // 更新文件列表
    const uploadFile: UploadFile = {
      uid: `paste-${Date.now()}`,
      name: file.name,
      status: 'done',
      size: file.size,
      type: file.type,
      url: previewUrl,
      originFileObj: rcFile
    };
    
    setLocalFileList([uploadFile]);
  };

  // 处理文件移除
  const handleRemove = () => {
    onFileChange(null);
    onImageUrlChange('');
    setLocalFileList([]);
    
    // 清理 URL 对象
    if (imageUrl && imageUrl.startsWith('blob:')) {
      URL.revokeObjectURL(imageUrl);
    }
    
    return true;
  };

  // 处理常规上传
  const handleUploadChange = (info: any) => {
    const { file, fileList: newFileList } = info;
    
    if (file.status !== 'removed') {
      onFileChange(file.originFileObj || file);
      
      // 创建预览URL
      if (file.originFileObj) {
        const previewUrl = URL.createObjectURL(file.originFileObj);
        onImageUrlChange(previewUrl);
      }
    }
    
    setLocalFileList(newFileList.slice(-1)); // 只保留最后一个文件
  };

  // 如果有图片，显示预览
  if (localFileList.length > 0 && imageUrl) {
    return (
      <div className="image-preview-container">
        <div className="image-preview" style={{ 
          position: 'relative', 
          textAlign: 'center',
          border: '1px dashed #d9d9d9',
          borderRadius: 6,
          padding: 16,
          background: '#fafafa'
        }}>
          <img 
            src={imageUrl} 
            alt="搜索图片" 
            style={{ 
              maxWidth: '100%', 
              maxHeight: 200, 
              objectFit: 'contain' 
            }} 
          />
          <div style={{ marginTop: 12 }}>
            <Space>
              <Button 
                icon={<DeleteOutlined />} 
                onClick={handleRemove}
                danger
                size="small"
              >
                移除图片
              </Button>
              <Button 
                icon={<FileImageOutlined />}
                size="small"
                onClick={() => {
                  // 重新打开文件选择
                  handleRemove();
                }}
              >
                重新选择
              </Button>
            </Space>
          </div>
        </div>
        
        <div style={{ marginTop: 8, fontSize: 12, color: '#999', textAlign: 'center' }}>
          <CopyOutlined /> 提示：您也可以直接复制其他图片并粘贴 (Ctrl+V) 来替换当前图片
        </div>
      </div>
    );
  }

  // 显示上传区域
  return (
    <div>
      <UploadDropzone
        fileList={localFileList}
        onChange={handleUploadChange}
        onRemove={handleRemove}
        onPasteUpload={handlePasteUpload}
        disabled={disabled}
        accept="image/*"
        maxSize={maxSize}
        multiple={false}
      />
    </div>
  );
};

export default ImageSearchUpload;
