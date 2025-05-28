import React, { useState, useEffect } from 'react';
import { Card, Form, Divider, message } from 'antd';
import type { UploadProps } from 'antd';
import { useNavigate } from 'react-router-dom';

// 导入类型
import { UploadFile, ImageMetadata, UploadResult } from './types';

// 导入组件
import UploadDropzone from './components/UploadDropzone';
import FileListView from './components/FileListView';
import MetadataModal from './components/MetadataModal';
import UploadResultDisplay from './components/UploadResultDisplay';
import BatchAnalyzeButton from './components/BatchAnalyzeButton';
import UploadToolbar from './components/UploadToolbar';

// 导入工具函数
import {
  fetchTagsData,
  analyzeImage,
  batchAnalyzeImages,
  uploadImages
} from './utils';
import { getImagePreviewUrl } from './previewUtils';

// 导入样式
import './styles/uploadPage.css';

/**
 * 图片上传页面
 * 包含拖拽上传区、文件列表、元数据编辑、AI分析和上传功能
 */
const UploadPage: React.FC = () => {
  // 表单实例，用于元数据编辑
  const [metadataForm] = Form.useForm();  const navigate = useNavigate();

  // 状态管理
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [availableTags, setAvailableTags] = useState<{ label: string; value: string }[]>([]);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [showMetadataModal, setShowMetadataModal] = useState(false);
  const [currentFile, setCurrentFile] = useState<UploadFile | null>(null);
  const [imageMetadataMap, setImageMetadataMap] = useState<Record<string, ImageMetadata>>({});
  const [hasUploaded, setHasUploaded] = useState(false);
  // 添加预览URL状态
  const [imagePreviewMap, setImagePreviewMap] = useState<Record<string, string>>({});

  // AI分析相关状态
  const [analyzingFile, setAnalyzingFile] = useState<UploadFile | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // 通用设置
  const [commonSettings] = useState({
    generateMetadata: true,
  });

  // 获取标签数据
  useEffect(() => {
    fetchTagsData(setAvailableTags);
  }, []);
  // 处理文件列表变化
  const handleFileListChange: UploadProps['onChange'] = ({ fileList }) => {
    const newList = [...fileList] as UploadFile[];

    // 初始化新添加文件的元数据
    newList.forEach(file => {
      if (!imageMetadataMap[file.uid]) {
        setImageMetadataMap(prev => ({
          ...prev,
          [file.uid]: {
            title: '',
            description: '',
            tags: [],
          }
        }));
      }

      // 生成图片预览URL
      if (file.originFileObj && !imagePreviewMap[file.uid]) {
        getImagePreviewUrl(file.originFileObj).then(url => {
          setImagePreviewMap(prev => ({
            ...prev,
            [file.uid]: url
          }));
        });
      }
    });

    setFileList(newList);
  };
  // 处理文件删除
  const handleFileRemove = (file: UploadFile) => {
    setFileList(prev => prev.filter(item => item.uid !== file.uid));
    // 删除对应的元数据
    setImageMetadataMap(prev => {
      const newMap = {...prev};
      delete newMap[file.uid];
      return newMap;
    });
    return true;
  };

  // AI分析图片
  const handleAnalyzeImage = async (file: UploadFile) => {
    await analyzeImage(file, setAnalyzingFile, setIsAnalyzing, setImageMetadataMap);
  };

  // 打开编辑元数据模态框
  const openMetadataModal = (file: UploadFile) => {
    setCurrentFile(file);

    // 设置表单初始值
    const metadata = imageMetadataMap[file.uid] || {
      title: '',
      description: '',
      tags: [],
      location: '',
      event: '',
    };

    metadataForm.setFieldsValue(metadata);
    setShowMetadataModal(true);
  };

  // 保存元数据
  const saveMetadata = () => {
    metadataForm.validateFields().then(values => {
      if (currentFile) {
        // 更新单个文件的元数据
        setImageMetadataMap(prev => ({
          ...prev,
          [currentFile.uid]: {
            ...prev[currentFile.uid],
            ...values,
          }
        }));
        message.success('元数据已更新');
      }

      setShowMetadataModal(false);
    });
  };

  // 上传图片
  const handleUpload = async () => {
    await uploadImages(
      fileList,
      imageMetadataMap,
      commonSettings,
      setUploading,
      setUploadProgress,
      setUploadResult,
      setHasUploaded
    );
  };

  // 批量AI分析所有图片
  const handleBatchAnalyze = async () => {
    await batchAnalyzeImages(
      fileList,
      setIsAnalyzing,
      setAnalyzingFile,
      setImageMetadataMap
    );
  };

  // 查看上传结果
  const handleViewUploaded = () => {
    navigate('/images');
  };
  // 重置上传表单
  const handleReset = () => {
    setFileList([]);
    setImageMetadataMap({});
    setUploadResult(null);
    setUploadProgress(0);
    setHasUploaded(false);
    // 清除图片预览URL
    setImagePreviewMap({});
  };

  return (
    <div className="upload-page">
      <Card title="上传图片" className="upload-card">
        {/* 上传区域 */}
        <UploadDropzone
          fileList={fileList}
          onChange={handleFileListChange}
          onRemove={handleFileRemove}
          disabled={uploading || hasUploaded}
        />

        {/* 操作按钮区域 - 移到文件列表上方 */}
        {fileList.length > 0 && (
          <>
            <Divider />

            {/* 批量AI分析按钮 */}
            <BatchAnalyzeButton
              fileList={fileList}
              isAnalyzing={isAnalyzing}
              hasUploaded={hasUploaded}
              onBatchAnalyze={handleBatchAnalyze}
            />

            {/* 上传工具栏 */}
            <UploadToolbar
              fileList={fileList}
              uploading={uploading}
              hasUploaded={hasUploaded}
              uploadProgress={uploadProgress}
              onUpload={handleUpload}
              onReset={handleReset}
            />
          </>
        )}

        {/* 文件列表 */}
        <div className="file-list-container">
          <FileListView
            fileList={fileList}
            imageMetadataMap={imageMetadataMap}
            isAnalyzing={isAnalyzing}
            analyzingFile={analyzingFile}
            disabled={uploading || hasUploaded}
            onAnalyzeImage={handleAnalyzeImage}
            openMetadataModal={openMetadataModal}
            onFileRemove={handleFileRemove}
          />
        </div>        {/* 元数据编辑模态框 */}
        <MetadataModal
          open={showMetadataModal}
          currentFile={currentFile}
          form={metadataForm}
          availableTags={availableTags}
          onSave={saveMetadata}
          onCancel={() => setShowMetadataModal(false)}
        />
      </Card>

      {/* 上传结果 */}
      <UploadResultDisplay
        result={uploadResult}
        onViewUploaded={handleViewUploaded}
        onReset={handleReset}
      />
    </div>
  );
};

export default UploadPage;
