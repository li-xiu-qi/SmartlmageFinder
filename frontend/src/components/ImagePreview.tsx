import React from 'react';
import { Image } from 'antd';
import { EyeOutlined } from '@ant-design/icons';
import { ImageDetail } from '@/types';

interface ImagePreviewProps {
  image: ImageDetail;
}

/**
 * 图片预览组件
 */
const ImagePreview: React.FC<ImagePreviewProps> = ({ image }) => {
  return (
    <div className="image-preview">
      <Image 
        src={image.filepath} 
        alt={image.title} 
        preview={{
          mask: <div>
            <EyeOutlined style={{ marginRight: 5 }} />
            点击查看大图
          </div>
        }}
        style={{ maxWidth: '100%' }}
      />
    </div>
  );
};

export default ImagePreview;
