import React from 'react';
import { Typography, Descriptions } from 'antd';
import { formatDate, formatFileSize } from '@/utils/format';
import { ImageDetail } from '@/types';

const { Title } = Typography;

interface FileInfoSectionProps {
  image: ImageDetail;
}

/**
 * 文件信息展示组件
 */
const FileInfoSection: React.FC<FileInfoSectionProps> = ({ image }) => {
  return (
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
  );
};

export default FileInfoSection;
