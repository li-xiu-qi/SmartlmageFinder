import React, { useState, useEffect } from 'react';
import { Drawer, Spin, message } from 'antd';
import { SearchX, Loader2 } from 'lucide-react';
import GalleryImageCard from '@/components/GalleryImageCard';
import SearchMetaBar from '@/components/SearchMetaBar';
import SharedImageDetail from '@/components/SharedImageDetail';
import { imageService } from '@/services/api';
import { ImageSearchResult, ImageDetail } from '@/types/models';

interface SearchResultsProps {
  loading: boolean;
  results: ImageSearchResult[];
  total: number;
  searchTime: number;
  searchKeyword?: string;
  referenceImage?: {
    id: number;
    title: string;
  };
}

/**
 * 搜索结果：画廊网格
 */
const SearchResults: React.FC<SearchResultsProps> = ({
  loading,
  results: initialResults,
  total,
  searchTime,
  searchKeyword,
  referenceImage,
}) => {
  const [selectedImage, setSelectedImage] = useState<ImageDetail | null>(null);
  const [isDrawerVisible, setIsDrawerVisible] = useState(false);
  const [drawerLoading, setDrawerLoading] = useState(false);
  const [currentResults, setCurrentResults] = useState<ImageSearchResult[]>(initialResults);

  useEffect(() => {
    setCurrentResults(initialResults);
  }, [initialResults]);

  const handleImageClick = async (imageItem: ImageSearchResult) => {
    setDrawerLoading(true);
    setIsDrawerVisible(true);
    try {
      const response = await imageService.getImageDetail({ image_id: imageItem.id });
      if (response.status === 'success' && response.data) {
        setSelectedImage(response.data);
      } else {
        message.error('加载图片详情失败');
        setIsDrawerVisible(false);
      }
    } catch (error) {
      console.error('获取图片详情失败:', error);
      message.error('加载图片详情失败');
      setIsDrawerVisible(false);
    } finally {
      setDrawerLoading(false);
    }
  };

  const handleDrawerClose = () => {
    setIsDrawerVisible(false);
    setSelectedImage(null);
  };

  const handleImageUpdate = (updatedImage: ImageDetail) => {
    setSelectedImage(updatedImage);
    setCurrentResults((prev) =>
      prev.map((item) => (item.id === updatedImage.id ? { ...item, title: updatedImage.title } : item))
    );
  };

  const handleImageDelete = (deletedImageId: number) => {
    setIsDrawerVisible(false);
    setSelectedImage(null);
    setCurrentResults((prev) => prev.filter((item) => item.id !== deletedImageId));
    message.success('图片已删除');
  };

  // 加载态
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 py-24 text-muted-foreground">
        <Loader2 className="h-7 w-7 animate-spin text-primary" strokeWidth={1.8} />
        <p className="text-sm">正在搜索，请稍候…</p>
      </div>
    );
  }

  // 空态
  if (currentResults.length === 0 && !loading) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed py-24 text-center">
        <SearchX className="h-10 w-10 text-muted-foreground/50" strokeWidth={1.5} />
        <p className="text-sm text-muted-foreground">
          {searchKeyword
            ? `没有找到与「${searchKeyword}」相关的图片`
            : '输入关键词，或上传一张图片开始搜索'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <SearchMetaBar total={total} searchTime={searchTime} referenceImage={referenceImage} />

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {currentResults.map((image) => (
          <GalleryImageCard
            key={image.id}
            image={image as never}
            showSimilarity
            onClick={() => handleImageClick(image)}
          />
        ))}
      </div>

      <Drawer
        title={selectedImage?.title || '图片详情'}
        placement="right"
        width={typeof window !== 'undefined' && window.innerWidth > 768 ? 640 : '100%'}
        onClose={handleDrawerClose}
        open={isDrawerVisible}
        destroyOnHidden
      >
        {drawerLoading ? (
          <div className="flex flex-col items-center justify-center gap-3 py-20 text-muted-foreground">
            <Spin />
            <p className="text-sm">正在加载详情…</p>
          </div>
        ) : (
          selectedImage && (
            <SharedImageDetail
              image={selectedImage}
              onUpdate={handleImageUpdate}
              onDelete={handleImageDelete}
              onClose={handleDrawerClose}
            />
          )
        )}
      </Drawer>
    </div>
  );
};

export default SearchResults;
