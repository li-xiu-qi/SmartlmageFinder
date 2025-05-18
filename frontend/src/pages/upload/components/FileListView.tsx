import React from 'react';
import { List, Space, Tag, Card, Typography, Empty } from 'antd';
import { UploadFile, ImageMetadata } from '../types';
import FileListItemActions from './FileListItemActions';
import FilePreview from './FilePreview';
import '../styles/fileList.css';

const { Text, Paragraph } = Typography;

interface FileListViewProps {
  fileList: UploadFile[];
  imageMetadataMap: Record<string, ImageMetadata>;
  isAnalyzing: boolean;
  analyzingFile: UploadFile | null;
  disabled?: boolean;
  onAnalyzeImage: (file: UploadFile) => void;
  openMetadataModal: (file: UploadFile) => void;
  onFileRemove: (file: UploadFile) => boolean;
}

/**
 * 文件列表视图组件
 * 显示所有已选择的文件及其元数据信息，提供操作按钮
 */
const FileListView: React.FC<FileListViewProps> = ({
  fileList,
  imageMetadataMap,
  isAnalyzing,
  analyzingFile,
  disabled = false,
  onAnalyzeImage,
  openMetadataModal,
  onFileRemove
}) => {
  if (fileList.length === 0) {
    return (
      <Empty 
        description="未选择文件" 
        image={Empty.PRESENTED_IMAGE_SIMPLE} 
      />
    );
  }

  return (
    <List
      itemLayout="horizontal"
      dataSource={fileList}
      renderItem={file => {
        // 获取当前文件的元数据
        const metadata = imageMetadataMap[file.uid] || {
          title: '',
          description: '',
          tags: []
        };

        return (
          <List.Item>
            <Card 
              size="small" 
              style={{ width: '100%' }}
              bodyStyle={{ padding: '12px' }}
            >
              <div className="file-item-container">                {/* 文件图标和名称或预览图 */}
                <FilePreview file={file} />

                {/* 文件元数据信息概览 */}
                <div className="file-metadata-container">
                  <div className="file-name">
                    <Text strong>{file.name}</Text>
                  </div>
                  
                  {metadata.title && (
                    <Paragraph ellipsis={{ rows: 1 }} className="file-metadata-item">
                      <Text type="secondary">标题: </Text>
                      <Text>{metadata.title}</Text>
                    </Paragraph>
                  )}
                  
                  {metadata.tags && metadata.tags.length > 0 && (
                    <Space size={[0, 4]} wrap className="file-tags-container">
                      {metadata.tags.map(tag => (
                        <Tag key={tag}>{tag}</Tag>
                      ))}
                    </Space>
                  )}
                </div>

                {/* 操作按钮 */}
                <FileListItemActions
                  file={file}
                  isAnalyzing={isAnalyzing}
                  analyzingFileUid={analyzingFile?.uid || null}
                  onAnalyze={onAnalyzeImage}
                  onEditMetadata={openMetadataModal}
                  onRemove={onFileRemove}
                  disabled={disabled}
                />
              </div>
            </Card>
          </List.Item>
        );
      }}
    />
  );
};

export default FileListView;
