import React, { useState, useEffect } from 'react';
import { Card, Spin, message, Drawer, Pagination } from 'antd';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { imageService, tagService } from '@/services/api';
import { TagInfo, ImageModel } from '@/types/models';
import { GetImagesListParams } from '@/types/image';
import { ImageCardModel, convertToImageCardModel } from '@/utils/typeConverters';
import FilterForm from './components/FilterForm';
import ViewControls, { ViewMode } from './components/ViewControls';
import ImageList from './components/ImageList';
import SharedImageDetail from '@/components/SharedImageDetail';
import './styles/components.less';

const ImagesPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // 状态定义
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState<ImageCardModel[]>([]);
  const [tags, setTags] = useState<TagInfo[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);  const [selectedImage, setSelectedImage] = useState<ImageModel | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [gridColumns, setGridColumns] = useState<number>(4);

  // 多选功能状态
  const [multiSelectMode, setMultiSelectMode] = useState(false);
  const [selectedImageIds, setSelectedImageIds] = useState<Set<number>>(new Set());
  const [batchDeleting, setBatchDeleting] = useState(false);

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
      // 将URL编码的标签解码并分割成数组
      const tagsArray = decodeURIComponent(tagsParam).split(',').map(tag => tag.trim());
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
  }, [page, pageSize, filterValues]);  // 处理筛选表单提交
  const handleFilterSubmit = (values: GetImagesListParams) => {
    setFilterValues(values);
    setPage(1); // 重置为第一页

    // 更新URL参数，以便分享和保存状态
    if (values.tags && Array.isArray(values.tags) && values.tags.length > 0) {
      navigate(`/images?tags=${encodeURIComponent(values.tags.join(','))}`, { replace: true });
    } else {
      navigate('/images', { replace: true });
    }
  };
  // 重置筛选条件
  const resetFilters = () => {
    setFilterValues({});
    setPage(1);
    // 重置URL
    navigate('/images', { replace: true });
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

  // 多选功能处理函数
  const toggleMultiSelectMode = () => {
    setMultiSelectMode(!multiSelectMode);
    setSelectedImageIds(new Set()); // 清空选择
  };

  const handleImageSelect = (imageId: number, selected: boolean) => {
    const newSelectedIds = new Set(selectedImageIds);
    if (selected) {
      newSelectedIds.add(imageId);
    } else {
      newSelectedIds.delete(imageId);
    }
    setSelectedImageIds(newSelectedIds);
  };

  const handleSelectAll = () => {
    if (selectedImageIds.size === images.length) {
      // 如果全部已选，则取消全选
      setSelectedImageIds(new Set());
    } else {
      // 否则全选当前页面的所有图片
      setSelectedImageIds(new Set(images.map(img => img.id)));
    }
  };

  const handleBatchDelete = async () => {
    if (selectedImageIds.size === 0) {
      message.warning('请选择要删除的图片');
      return;
    }

    try {
      setBatchDeleting(true);
      const imageIds = Array.from(selectedImageIds);
      const response = await imageService.batchDeleteImages({ image_ids: imageIds });

      if (response.status === 'success' && response.data) {
        const { success_count, failed_count, failed_ids } = response.data;

        if (success_count > 0) {
          message.success(`成功删除 ${success_count} 张图片`);

          // 更新图片列表，移除已删除的图片
          setImages(prevImages =>
            prevImages.filter(img => !imageIds.includes(img.id) || failed_ids.includes(img.id))
          );
          setTotal(prev => prev - success_count);
        }

        if (failed_count > 0) {
          message.warning(`有 ${failed_count} 张图片删除失败`);
        }

        // 清空选择
        setSelectedImageIds(new Set());

        // 如果当前页没有图片了，回到上一页
        const remainingImages = images.filter(img => !imageIds.includes(img.id) || failed_ids.includes(img.id));
        if (remainingImages.length === 0 && page > 1) {
          setPage(page - 1);
        }
      }
    } catch (error) {
      console.error('批量删除失败:', error);
      message.error('批量删除失败');
    } finally {
      setBatchDeleting(false);
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

      // 更新URL，方便分享和保存状态
      navigate(`/images?tags=${encodeURIComponent(updatedTags.join(','))}`, { replace: true });
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
          multiSelectMode={multiSelectMode}
          selectedCount={selectedImageIds.size}
          onToggleMultiSelect={toggleMultiSelectMode}
          onSelectAll={handleSelectAll}
          onBatchDelete={handleBatchDelete}
          batchDeleting={batchDeleting}
        />
          <ImageList
          images={images}
          viewMode={viewMode}
          gridColumns={gridColumns}
          onImageClick={handleImageClick}
          onTagClick={handleTagClick}
          onDeleteImage={handleDeleteImage}
          multiSelectMode={multiSelectMode}
          selectedImageIds={selectedImageIds}
          onImageSelect={handleImageSelect}
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
            destroyOnHidden          >
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
