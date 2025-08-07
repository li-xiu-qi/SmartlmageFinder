import React from 'react';
import { Button, Progress, Space, Tooltip } from 'antd';
import { CloudUploadOutlined, ReloadOutlined } from '@ant-design/icons';
import { UploadFile } from '../types';

interface UploadToolbarProps {
  fileList: UploadFile[]; // 文件列表
  uploading: boolean; // 是否正在上传
  hasUploaded: boolean; // 是否已上传完成
  uploadProgress: number; // 上传进度 (0-100)
  onUpload: () => void; // 上传按钮点击回调
  onReset: () => void; // 重置按钮点击回调
}

/**
 * 上传工具栏组件
 * 包含上传按钮、进度条和重置按钮
 */
const UploadToolbar: React.FC<UploadToolbarProps> = ({
  fileList,
  uploading,
  hasUploaded,
  uploadProgress,
  onUpload,
  onReset
}) => {
  // 上传按钮状态计算
  const isUploadDisabled = fileList.length === 0 || uploading || hasUploaded;
  
  // 获取上传按钮的提示文本
  const getUploadTooltip = () => {
    if (fileList.length === 0) {
      return '请先选择图片后再上传';
    }
    
    if (uploading) {
      return '正在上传中...';
    }
    
    if (hasUploaded) {
      return '图片已上传，如需再次上传请先重置';
    }
    
    return '将选中的图片上传到服务器';
  };

  return (
    <div className="upload-toolbar" style={{ marginTop: 16 }}>
      {/* 上传进度条 */}
      {uploading && (
        <Progress 
          percent={uploadProgress} 
          status="active" 
          style={{ marginBottom: 16 }}
        />
      )}
      
      {/* 按钮区域 */}
      <Space size="middle" style={{ display: 'flex', justifyContent: 'center' }}>
        <Tooltip 
          title={getUploadTooltip()}
          getPopupContainer={(trigger) => trigger.parentElement || document.body}
        >
          <Button
            type="primary"
            icon={<CloudUploadOutlined />}
            loading={uploading}
            onClick={onUpload}
            disabled={isUploadDisabled}
            size="large"
          >
            {uploading ? '上传中...' : '上传图片'}
          </Button>
        </Tooltip>
        
        <Tooltip 
          title="清空当前选择，重新开始"
          getPopupContainer={(trigger) => trigger.parentElement || document.body}
        >
          <Button
            icon={<ReloadOutlined />}
            onClick={onReset}
            disabled={uploading}
            size="large"
          >
            重置
          </Button>
        </Tooltip>
      </Space>
    </div>
  );
};

export default UploadToolbar;
