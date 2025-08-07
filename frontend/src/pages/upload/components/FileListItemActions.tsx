import React from 'react';
import { Button, Tooltip, Spin, Popconfirm } from 'antd';
import { EditOutlined, ExperimentOutlined, DeleteOutlined, LoadingOutlined } from '@ant-design/icons';
import { UploadFile } from '../types';

interface FileListItemActionsProps {
  file: UploadFile;
  isAnalyzing: boolean;
  analyzingFileUid: string | null;
  onAnalyze: (file: UploadFile) => void;
  onEditMetadata: (file: UploadFile) => void;
  onRemove: (file: UploadFile) => void;
  disabled?: boolean;
}

const FileListItemActions: React.FC<FileListItemActionsProps> = ({
  file,
  isAnalyzing,
  analyzingFileUid,
  onAnalyze,
  onEditMetadata,
  onRemove,
  disabled
}) => {
  const isCurrentFileAnalyzing = isAnalyzing && analyzingFileUid === file.uid;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <Tooltip 
        title="AI分析图片"
        getPopupContainer={(trigger) => trigger.parentElement || document.body}
      >
        <Button
          icon={isCurrentFileAnalyzing ? <Spin indicator={<LoadingOutlined style={{ fontSize: 14 }} spin />} /> : <ExperimentOutlined />}
          onClick={() => onAnalyze(file)}
          size="small"
          disabled={disabled || isAnalyzing}
        />
      </Tooltip>
      <Tooltip 
        title="编辑元数据"
        getPopupContainer={(trigger) => trigger.parentElement || document.body}
      >
        <Button
          icon={<EditOutlined />}
          onClick={() => onEditMetadata(file)}
          size="small"
          disabled={disabled}
        />
      </Tooltip>
      <Popconfirm
        title={`确定移除文件 ${file.name} 吗?`}
        onConfirm={() => onRemove(file)}
        okText="确定"
        cancelText="取消"
        disabled={disabled}
      >
        <Button
          icon={<DeleteOutlined />}
          danger
          size="small"
          disabled={disabled}
        />
      </Popconfirm>
    </div>
  );
};

export default FileListItemActions;
