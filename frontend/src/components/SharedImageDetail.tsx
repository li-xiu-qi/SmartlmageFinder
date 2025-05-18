import React, { useState } from 'react';
import { Spin, message } from 'antd';
import { imageService, searchService, metadataService } from '@/services/api';
import { ImageDetail, ImageSearchResult } from '@/types';
import { VectorType } from '@/types/search'; // Changed from VectorSearchTarget to VectorType
import ImagePreview from '@/components/ImagePreview';
import EditableField from '@/components/EditableField';
import FileInfoSection from '@/components/FileInfoSection';
import TagsSection from '@/components/TagsSection';
import MetadataSection from '@/components/MetadataSection';
import ActionsPanel from '@/components/ActionsPanel';
import SimilarImagesModal from '@/components/SimilarImagesModal';
import './shared-image-detail.less';

interface SharedImageDetailProps {
  image: ImageDetail;
  onUpdate: (image: ImageDetail) => void;
  onDelete: (id: number) => void;
  onClose?: () => void; // 可选的关闭回调
}

/**
 * 共享的图片详情组件
 * 该组件可以在多个地方重用，包括图片列表页、首页最近图片等
 */
const SharedImageDetail: React.FC<SharedImageDetailProps> = ({ 
  image, 
  onUpdate, 
  onDelete,
  onClose 
}) => {
  const [loading, setLoading] = useState(false);
  const [similarImages, setSimilarImages] = useState<ImageSearchResult[]>([]);
  const [showSimilarModal, setShowSimilarModal] = useState(false);
  // Changed type and initial value to use VectorType
  const [searchTarget, setSearchTarget] = useState<VectorType>(VectorType.IMAGE); 
  
  // Changed parameter type to VectorType
  const handleSearchTargetChange = (value: VectorType) => { 
    setSearchTarget(value);
  };
  
  // 更新标题
  const handleUpdateTitle = async (newTitle: string) => {
    if (newTitle.trim() === '') {
      message.error('标题不能为空');
      return;
    }

    try {
      setLoading(true);
      const response = await imageService.updateImage({ image_id: image.id, title: newTitle });
      if (response.status === 'success') {
        message.success('标题更新成功');
        onUpdate({ ...image, title: newTitle });
      }
    } catch (error) {
      console.error('更新标题失败:', error);
      message.error('更新标题失败');
    } finally {
      setLoading(false);
    }
  };

  // 更新描述
  const handleUpdateDescription = async (newDescription: string) => {
    try {
      setLoading(true);
      const response = await imageService.updateImage({ image_id: image.id, description: newDescription });
      if (response.status === 'success') {
        message.success('描述更新成功');
        onUpdate({ ...image, description: newDescription });
      }
    } catch (error) {
      console.error('更新描述失败:', error);
      message.error('更新描述失败');
    } finally {
      setLoading(false);
    }
  };

  // 更新元数据
  const handleMetadataUpdate = async (updatedMetadata: Record<string, string>) => {
    try {
      setLoading(true);
      const response = await metadataService.updateMetadata({ 
        image_id: image.id, 
        metadata: updatedMetadata 
      });
      if (response.status === 'success' && response.data) {
        message.success('元数据更新成功');
        onUpdate({ ...image, metadata: response.data.metadata }); // 使用返回的图片数据中的元数据
      } else {
        message.error(response.error?.message || '元数据更新失败');
      }
    } catch (error: unknown) { // 使用 unknown 类型以提高类型安全性
      console.error('更新元数据失败:', error);
      let errorMessage = '更新元数据时发生未知错误';
      if (error instanceof Error) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else if (typeof error === 'object' && error !== null && 'message' in error) {
        // 安全地尝试访问 error.message
        const errObj = error as { message?: unknown };
        if (typeof errObj.message === 'string') {
          errorMessage = errObj.message;
        }
      }
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // 获取相似图片
  const fetchSimilarImages = async () => {
    try {
      setLoading(true);
      setShowSimilarModal(true);
      
      // 使用新的 vector_type 参数调用相似图片搜索服务
      const response = await searchService.similarSearch(image.id, { 
        vector_type: searchTarget, // 使用 searchTarget 作为 vector_type 的值
        limit: 12
        // 移除了 search_targets 和 search_type
      });
      
      if (response.status === 'success' && response.data) {
        // 过滤掉当前图片
        const filtered = response.data.filter(img => img.id !== image.id);
        setSimilarImages(filtered);
      }
    } catch (error) {
      console.error('获取相似图片失败:', error);
      message.error('获取相似图片失败');
    } finally {
      setLoading(false);
    }
  };

  // 标签更新处理
  const handleTagsUpdate = (tags: string[]) => {
    onUpdate({ ...image, tags });
  };

  // 处理图片删除，如果提供了onClose则调用
  const handleDelete = (id: number) => {
    onDelete(id);
    if (onClose) {
      onClose();
    }
  };

  return (
    <div className="image-detail-container">
      <Spin spinning={loading}>
        {/* 图片预览 */}
        <ImagePreview image={image} />
        
        {/* 标题和描述 */}
        <div className="detail-section">
          <EditableField 
            value={image.title} 
            onSave={handleUpdateTitle}
            title={true}
            loading={loading}
          />
          
          <EditableField 
            value={image.description || ''} 
            onSave={handleUpdateDescription}
            loading={loading}
          />
        </div>
        
        {/* 文件信息 */}
        <FileInfoSection image={image} />
          {/* 标签管理 */}
        <TagsSection 
          imageId={image.id} 
          tags={image.tags} 
          onTagsUpdate={handleTagsUpdate} 
        />
        
        {/* 元数据展示 */}
        <MetadataSection 
          metadata={image.metadata || {}} 
          onMetadataUpdate={handleMetadataUpdate} // 传递处理函数
          loading={loading} // 传递 loading 状态
        />
          {/* 操作按钮 */}
        <ActionsPanel 
          image={image}
          searchType={searchTarget as string} 
          // Changed cast to VectorType
          onSearchTypeChange={(value) => handleSearchTargetChange(value as VectorType)} 
          onFindSimilar={fetchSimilarImages}
          onDelete={handleDelete}
          onUpdate={onUpdate}
          loading={loading}
        />
        
        {/* 相似图片模态框 */}
        <SimilarImagesModal 
          open={showSimilarModal}
          onClose={() => setShowSimilarModal(false)}
          loading={loading}
          searchTarget={searchTarget} // 修改属性名
          onSearchTargetChange={handleSearchTargetChange} // 修改属性名和传递的函数
          onSearch={fetchSimilarImages}
          similarImages={similarImages}
        />
      </Spin>
    </div>
  );
};

export default SharedImageDetail;
