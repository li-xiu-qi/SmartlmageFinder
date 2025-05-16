import React from 'react';
import { Button, Tooltip } from 'antd';
import { ExperimentOutlined, SyncOutlined } from '@ant-design/icons';
import { UploadFile } from '../types';

interface BatchAnalyzeButtonProps {
  fileList: UploadFile[]; // 文件列表
  isAnalyzing: boolean; // 是否正在进行AI分析
  hasUploaded: boolean; // 是否已经上传过文件
  onBatchAnalyze: () => void; // 批量分析回调
}

/**
 * 批量AI分析按钮组件
 * 提供一键对所有选中图片进行AI分析的功能
 */
const BatchAnalyzeButton: React.FC<BatchAnalyzeButtonProps> = ({
  fileList,
  isAnalyzing,
  hasUploaded,
  onBatchAnalyze
}) => {
  // 判断按钮是否应该被禁用
  const isDisabled = fileList.length === 0 || isAnalyzing || hasUploaded;
  
  // 根据不同状态显示相应的提示信息
  const getTooltipText = () => {
    if (fileList.length === 0) {
      return '请先选择图片';
    }
    
    if (isAnalyzing) {
      return 'AI分析进行中...';
    }
    
    if (hasUploaded) {
      return '图片已上传，如需分析请重新选择图片';
    }
    
    return '使用AI分析所有选中的图片，自动生成标题、描述和标签';
  };

  return (
    <div className="batch-analyze-container" style={{ marginBottom: 16 }}>
      <Tooltip title={getTooltipText()}>
        <Button 
          type="default"
          icon={isAnalyzing ? <SyncOutlined spin /> : <ExperimentOutlined />}
          onClick={onBatchAnalyze}
          disabled={isDisabled}
          loading={isAnalyzing}
          block
        >
          {isAnalyzing ? 'AI分析进行中...' : '批量AI分析图片'}
        </Button>
      </Tooltip>
    </div>
  );
};

export default BatchAnalyzeButton;
