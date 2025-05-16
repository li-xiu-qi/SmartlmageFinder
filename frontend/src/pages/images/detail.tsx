import React, { useState } from 'react';
import { Spin, message } from 'antd';
import { imageService, searchService } from '@/services/api';
import { ImageDetail, ImageSearchResult } from '@/types';
import ImagePreview from './components/ImagePreview';
import EditableField from './components/EditableField';
import FileInfoSection from './components/FileInfoSection';
import TagsSection from './components/TagsSection';
import MetadataSection from './components/MetadataSection';
import ActionsPanel from './components/ActionsPanel';
import SimilarImagesModal from './components/SimilarImagesModal';
import './components/detail.less';

interface ImageDetailViewProps {
  image: ImageDetail;
  onUpdate: (image: ImageDetail) => void;
  onDelete: (uuid: string) => void;
}

/**
 * 图片详情页面组件
 */
const ImageDetailView: React.FC<ImageDetailViewProps> = ({ image, onUpdate, onDelete }) => {
  const [loading, setLoading] = useState(false);
  const [similarImages, setSimilarImages] = useState<ImageSearchResult[]>([]);
  const [showSimilarModal, setShowSimilarModal] = useState(false);
  const [searchType, setSearchType] = useState<string>('image');
  
  // 更新标题
  const handleUpdateTitle = async (newTitle: string) => {
    if (newTitle.trim() === '') {
      message.error('标题不能为空');
      return;
    }

    try {
      setLoading(true);
      const response = await imageService.updateImage(image.uuid, { title: newTitle });
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
      const response = await imageService.updateImage(image.uuid, { description: newDescription });
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
      
      // 使用match_modes参数代替search_type以符合后端API要求
      const response = await searchService.searchSimilar(image.uuid, { 
        limit: 12,
        match_modes: [searchType] // 将单个值改为数组形式发送
      });
      
      if (response.status === 'success' && response.data) {
        // 过滤掉当前图片
        const filtered = response.data.results.filter(img => img.uuid !== image.uuid);
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

  return (
    <div className="image-detail-drawer">
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
            value={image.description} 
            onSave={handleUpdateDescription}
            loading={loading}
          />
        </div>
        
        {/* 文件信息 */}
        <FileInfoSection image={image} />
        
        {/* 标签管理 */}
        <TagsSection 
          uuid={image.uuid} 
          tags={image.tags} 
          onTagsUpdate={handleTagsUpdate} 
        />
        
        {/* 元数据展示 */}
        <MetadataSection metadata={image.metadata || {}} />
        
        {/* 操作按钮 */}
        <ActionsPanel 
          image={image}
          searchType={searchType}
          onSearchTypeChange={setSearchType}
          onFindSimilar={fetchSimilarImages}
          onDelete={onDelete}
          onUpdate={onUpdate}
          loading={loading}
        />
        
        {/* 相似图片模态框 */}
        <SimilarImagesModal 
          open={showSimilarModal}
          onClose={() => setShowSimilarModal(false)}
          loading={loading}
          searchType={searchType}
          onSearchTypeChange={setSearchType}
          onSearch={fetchSimilarImages}
          similarImages={similarImages}
        />
      </Spin>
    </div>
  );
};

export default ImageDetailView;
