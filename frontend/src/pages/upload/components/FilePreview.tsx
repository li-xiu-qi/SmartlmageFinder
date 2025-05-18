import React, { useState, useEffect } from 'react';
import { Image } from 'antd';
import { PictureOutlined } from '@ant-design/icons';
import { UploadFile } from '../types';
import '../styles/fileList.css';

/**
 * 从文件获取图片预览URL
 * @param file 图片文件
 * @returns 预览URL Promise
 */
const getImagePreviewUrl = (file: File): Promise<string> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result as string);
  });
};

interface FilePreviewProps {
  file: UploadFile;
}

/**
 * 文件预览组件
 * 显示上传文件的预览图
 */
const FilePreview: React.FC<FilePreviewProps> = ({ file }) => {
  const [previewUrl, setPreviewUrl] = useState<string>('');
  
  useEffect(() => {
    // 当文件变化时，生成预览URL
    if (file.originFileObj) {
      getImagePreviewUrl(file.originFileObj).then(url => {
        setPreviewUrl(url);
      }).catch(error => {
        console.error('生成预览失败:', error);
      });
    }
  }, [file]);

  return (
    <div className="file-preview-container">
      {previewUrl ? (
        <Image 
          src={previewUrl} 
          alt={file.name}
          className="file-preview-image"
          preview={{ 
            mask: <div>预览</div>
          }}
        />
      ) : (
        <PictureOutlined className="file-icon" />
      )}
    </div>
  );
};

export default FilePreview;
