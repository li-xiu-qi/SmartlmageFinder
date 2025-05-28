import React from 'react';
import { Button, Dropdown, Tooltip, Space } from 'antd';
import { ExperimentOutlined, SyncOutlined, DownOutlined } from '@ant-design/icons';
import { UploadFile, ImageMetadata, AnalysisMode } from '../types';
import type { MenuProps } from 'antd';

interface BatchAnalyzeButtonProps {
  fileList: UploadFile[]; // 文件列表
  imageMetadataMap: Record<string, ImageMetadata>; // 图片元数据映射
  isAnalyzing: boolean; // 是否正在进行AI分析
  hasUploaded: boolean; // 是否已经上传过文件
  onBatchAnalyze: (mode: AnalysisMode) => void; // 批量分析回调
}

/**
 * 批量AI分析按钮组件
 * 提供一键对所有选中图片或未分析图片进行AI分析的功能
 */
const BatchAnalyzeButton: React.FC<BatchAnalyzeButtonProps> = ({
  fileList,
  imageMetadataMap,
  isAnalyzing,
  hasUploaded,
  onBatchAnalyze
}) => {
  // 判断按钮是否应该被禁用
  const isDisabled = fileList.length === 0 || isAnalyzing || hasUploaded;

  // 计算已分析和未分析的图片数量
  const getAnalysisStats = () => {
    const analyzedCount = fileList.filter(file => {
      const metadata = imageMetadataMap[file.uid];
      return metadata && (metadata.title || metadata.description || metadata.tags.length > 0);
    }).length;

    const unanalyzedCount = fileList.length - analyzedCount;

    return { analyzedCount, unanalyzedCount };
  };

  const { analyzedCount, unanalyzedCount } = getAnalysisStats();

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

    return `当前共 ${fileList.length} 张图片，已分析 ${analyzedCount} 张，未分析 ${unanalyzedCount} 张`;
  };

  // 下拉菜单选项
  const menuItems: MenuProps['items'] = [
    {
      key: AnalysisMode.ALL,
      label: (
        <span>
          分析全部图片 ({fileList.length}张)
        </span>
      ),
      disabled: isDisabled || fileList.length === 0,
    },
    {
      key: AnalysisMode.UNANALYZED_ONLY,
      label: (
        <span>
          仅分析未分析图片 ({unanalyzedCount}张)
        </span>
      ),
      disabled: isDisabled || unanalyzedCount === 0,
    },
  ];

  // 处理菜单点击
  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    onBatchAnalyze(key as AnalysisMode);
  };

  return (
    <div className="batch-analyze-container" style={{ marginBottom: 16 }}>
      <Tooltip title={getTooltipText()}>
        <Dropdown
          menu={{ items: menuItems, onClick: handleMenuClick }}
          disabled={isDisabled}
          trigger={['click']}
        >
          <Button
            type="default"
            icon={isAnalyzing ? <SyncOutlined spin /> : <ExperimentOutlined />}
            disabled={isDisabled}
            loading={isAnalyzing}
            block
          >
            <Space>
              {isAnalyzing ? 'AI分析进行中...' : '批量AI分析图片'}
              {!isAnalyzing && <DownOutlined />}
            </Space>
          </Button>
        </Dropdown>
      </Tooltip>
    </div>
  );
};

export default BatchAnalyzeButton;
