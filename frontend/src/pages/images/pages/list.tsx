import React, { useState, useEffect } from 'react';
import { Card, Spin, message, Drawer, Pagination } from 'antd';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { imageService, tagService, searchService, aiService } from '@/services/api';
import { TagInfo, ImageModel } from '@/types/models';
import { GetImagesListParams } from '@/types/image';
import { ImageCardModel, convertToImageCardModel } from '@/utils/typeConverters';
import { VectorSearchTarget, SearchType } from '@/types/search';
import { AnalysisDetailLevel } from '@/types/ai';
import FilterForm from '../components/FilterForm';
import ViewControls, { ViewMode } from '../components/ViewControls';
import ImageList from '../components/ImageList';
import SharedImageDetail from '@/components/SharedImageDetail';
import '../styles/components.less';

const ImagesPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // 状态定义
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState<ImageCardModel[]>([]);
  const [tags, setTags] = useState<TagInfo[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [selectedImage, setSelectedImage] = useState<ImageModel | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [gridColumns, setGridColumns] = useState<number>(2);

  // 筛选条件
  const [filterValues, setFilterValues] = useState<GetImagesListParams>({});

  // 获取热门标签
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const response = await tagService.getPopularTags({ limit: 50 });
        if (response.status === 'success' && response.data) {
          setTags(response.data);
        }
      } catch (error) {
        console.error('获取标签失败:', error);
      }
    };

    fetchTags();
  }, []);

  // 处理URL中的查询参数
  useEffect(() => {
    const tagsParam = searchParams.get('tags');
    if (tagsParam) {
      const tagsArray = tagsParam.split(',').map(tag => tag.trim());
      setFilterValues(prev => ({ ...prev, tags: tagsArray }));
    }
  }, [searchParams]);

  // 获取图片数据
  useEffect(() => {
    const fetchImages = async () => {
      try {
        setLoading(true);
        const params: GetImagesListParams = {
          ...filterValues,
          page,
          page_size: pageSize,
        };

        const response = await imageService.getImagesList(params);
        if (response.status === 'success' && response.data) {
          // 将API返回的ImageModel转换为前端显示所需的ImageCardModel
          const imageCards = response.data.map(img => convertToImageCardModel(img));
          setImages(imageCards);
          
          if (response.metadata && response.metadata.pagination) {
            setTotal(response.metadata.pagination.total_items);
          }
        }
      } catch (error) {
        console.error('获取图片失败:', error);
        message.error('获取图片数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, [page, pageSize, filterValues]);

  // 处理筛选表单提交
  const handleFilterSubmit = (values: GetImagesListParams) => {
    setFilterValues(values);
    setPage(1); // 重置为第一页
  };

  // 重置筛选条件
  const resetFilters = () => {
    setFilterValues({});
    setPage(1);
  };

  // 处理图片点击事件，打开详情抽屉
  const handleImageClick = async (image: ImageCardModel) => {
    try {
      setLoading(true);
      const response = await imageService.getImageDetail({ image_id: image.id });
      if (response.status === 'success' && response.data) {
        setSelectedImage(response.data);
        setDetailVisible(true);
      }
    } catch (error) {
      console.error('获取图片详情失败:', error);
      message.error('获取图片详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 关闭详情抽屉
  const handleDetailClose = () => {
    setDetailVisible(false);
    setSelectedImage(null);
  };

  // 删除图片
  const handleDeleteImage = async (id: number) => {
    try {
      setLoading(true);
      const response = await imageService.deleteImage({ image_id: id });
      if (response.status === 'success') {
        message.success('图片删除成功');
        // 重新获取当前页的数据
        const updatedImages = images.filter(img => img.id !== id);
        if (updatedImages.length === 0 && page > 1) {
          setPage(page - 1);
        } else {
          setImages(updatedImages);
          setTotal(prev => prev - 1);
        }
        // 关闭详情抽屉
        setDetailVisible(false);
      }
    } catch (error) {
      console.error('删除图片失败:', error);
      message.error('删除图片失败');
    } finally {
      setLoading(false);
    }
  };

  // 更新图片信息
  const handleImageUpdate = (updatedImage: ImageModel) => {
    setSelectedImage(updatedImage);
    
    // 更新列表中的图片数据
    setImages(prevImages => 
      prevImages.map(img => 
        img.id === updatedImage.id 
          ? convertToImageCardModel(updatedImage) 
          : img
      )
    );
  };

  // 查找相似图片
  const handleFindSimilar = async (imageId: number, searchTarget: VectorSearchTarget) => {
    try {
      const params = {
        search_type: SearchType.VECTOR,
        search_targets: [searchTarget],
        limit: 12
      };
      
      const response = await searchService.similarSearch(imageId, params);
      if (response.status === 'success' && response.data) {
        return response.data;
      }
      return [];
    } catch (error) {
      console.error('查找相似图片失败:', error);
      throw error;
    }
  };

  // AI分析生成内容
  const handleAIAnalyze = async (imageId: number) => {
    try {
      const response = await aiService.analyzeExistingImage(
        imageId, 
        { detail: AnalysisDetailLevel.HIGH }
      );
      
      if (response.status === 'success' && response.data) {
        return {
          title: response.data.title,
          description: response.data.description,
          tags: response.data.tags
        };
      }
      
      throw new Error('AI分析失败');
    } catch (error) {
      console.error('AI分析失败:', error);
      throw error;
    }
  };

  // 更新标签
  const handleUpdateTags = async (id: number, tags: string[]) => {
    try {
      const response = await imageService.updateImage({
        image_id: id,
        tags: tags
      });
      
      if (response.status === 'success' && response.data) {
        return response.data.tags;
      }
      
      throw new Error('更新标签失败');
    } catch (error) {
      console.error('更新标签失败:', error);
      throw error;
    }
  };

  // 处理标签点击
  const handleTagClick = (tag: string) => {
    // 设置筛选条件
    const updatedTags = [...(filterValues.tags || [])];
    if (!updatedTags.includes(tag)) {
      updatedTags.push(tag);
      setFilterValues(prev => ({ ...prev, tags: updatedTags }));
      setPage(1);
    }
  };

  return (
    <div className="images-page">
      <Spin spinning={loading}>
        <Card className="filter-card">
          <FilterForm 
            tags={tags}
            onFilter={handleFilterSubmit}
            onReset={resetFilters}
            initialValues={filterValues}
            loading={loading}
          />
        </Card>
        
        <ViewControls 
          total={total}
          viewMode={viewMode}
          gridColumns={gridColumns}
          onViewModeChange={setViewMode}
          onGridColumnsChange={setGridColumns}
        />
        
        <ImageList 
          images={images}
          viewMode={viewMode}
          gridColumns={gridColumns}
          onImageClick={handleImageClick}
          onTagClick={handleTagClick}
          onDeleteImage={handleDeleteImage}
          loading={loading}
        />
        
        {total > 0 && (
          <div className="pagination-container">
            <Pagination
              current={page}
              pageSize={pageSize}
              total={total}
              onChange={(p, ps) => {
                setPage(p);
                setPageSize(ps);
              }}
              showSizeChanger
              showQuickJumper
              showTotal={total => `共 ${total} 张图片`}
            />
          </div>
        )}

        {/* 图片详情抽屉 */}
        {selectedImage && (
          <Drawer
            title="图片详情"
            placement="right"
            closable={true}
            onClose={handleDetailClose}
            open={detailVisible}
            width={640}
            destroyOnClose          >            
            <SharedImageDetail 
              image={selectedImage} 
              onUpdate={handleImageUpdate} 
              onDelete={handleDeleteImage}
              onClose={handleDetailClose}
            />
          </Drawer>
        )}      </Spin>
    </div>
  );
};

export default ImagesPage;