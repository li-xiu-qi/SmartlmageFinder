import React, { useState } from 'react';
import { Spin, message } from 'antd';
import { imageService, searchService } from '@/services/api';
import { ImageDetail, ImageSearchResult } from '@/types';
import { VectorSearchTarget, SearchType } from '@/types/search';
import ImagePreview from '@/components/ImagePreview';
import EditableField from '@/components/EditableField';
import FileInfoSection from '@/components/FileInfoSection';
import TagsSection from '@/components/TagsSection';
import MetadataSection from '@/components/MetadataSection';
import ActionsPanel from '@/components/ActionsPanel';
import SimilarImagesModal from '@/pages/images/components/SimilarImagesModal';
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
  const [searchType, setSearchType] = useState<string>('image');
  
  // 处理搜索类型变更
  const handleSearchTypeChange = (value: string) => {
    setSearchType(value);
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
  // 获取相似图片
  const fetchSimilarImages = async () => {
    try {
      setLoading(true);
      setShowSimilarModal(true);
      
      // 将searchType字符串映射到VectorSearchTarget枚举
      let targetType: VectorSearchTarget;
      switch (searchType) {
        case 'title':
          targetType = VectorSearchTarget.TITLE;
          break;
        case 'description':
          targetType = VectorSearchTarget.DESCRIPTION;
          break;
        case 'image':
        default:
          targetType = VectorSearchTarget.IMAGE;
          break;
      }
      
      const response = await searchService.similarSearch(image.id, { 
        search_targets: [targetType], 
        limit: 12,
        search_type: SearchType.VECTOR // 使用向量搜索
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
        <MetadataSection metadata={image.metadata || {}} />
          {/* 操作按钮 */}
        <ActionsPanel 
          image={image}
          searchType={searchType}
          onSearchTypeChange={handleSearchTypeChange}
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
          searchType={searchType}
          onSearchTypeChange={handleSearchTypeChange}
          onSearch={fetchSimilarImages}
          similarImages={similarImages}
        />
      </Spin>
    </div>
  );
};

export default SharedImageDetail;
