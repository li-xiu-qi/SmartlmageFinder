import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, ScanSearch, ArrowRight, Images as ImagesIcon, Tags as TagsIcon } from 'lucide-react';
import { Drawer, message } from 'antd';

import { ImageDetail, TagInfo } from '@/types/models';
import { SystemStats } from './types';

import { imageService, tagService, systemService } from '@/services/api';
import SharedImageDetail from '@/components/SharedImageDetail';
import GalleryImageCard from '@/components/GalleryImageCard';
import { Button } from '@/components/ui/button';

/**
 * 首页：画廊导向
 * 顶部欢迎 + 快捷动作，主体是最近上传的图片网格，弱化运维统计
 */
const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [recentImages, setRecentImages] = useState<ImageDetail[]>([]);
  const [popularTags, setPopularTags] = useState<TagInfo[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats>({
    totalImages: 0,
    status: 'unknown',
    totalTags: 0,
  });

  const [selectedImage, setSelectedImage] = useState<ImageDetail | null>(null);
  const [drawerVisible, setDrawerVisible] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [imagesResponse, tagsResponse, infoResponse, databaseResponse, storageResponse, cacheResponse] =
          await Promise.all([
            imageService.getImagesList({ page: 1, page_size: 12, sort_by: 'created_at', order: 'desc' }),
            tagService.getPopularTags({ limit: 20 }).catch(() => ({ status: 'error', data: [] })),
            systemService.getSystemInfo(),
            systemService.getDatabaseInfo(),
            systemService.getStorageInfo(),
            systemService.getCacheInfo(),
          ]);

        if (imagesResponse.status === 'success' && imagesResponse.data) {
          setRecentImages(imagesResponse.data);
        }
        if (tagsResponse.status === 'success' && tagsResponse.data) {
          setPopularTags(tagsResponse.data);
        }
        if (
          infoResponse.status === 'success' &&
          storageResponse.status === 'success' &&
          databaseResponse.status === 'success' &&
          cacheResponse.status === 'success'
        ) {
          setSystemStats({
            totalImages: storageResponse.data.total_images,
            status: infoResponse.data.status,
            totalTags: storageResponse.data.total_tags,
          });
        } else {
          setSystemStats((prev) => ({ ...prev, status: 'error' }));
        }
      } catch (error) {
        console.error('获取首页数据失败:', error);
        setSystemStats({ totalImages: 0, status: 'error', totalTags: 0 });
        setRecentImages([]);
        setPopularTags([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleImageClick = async (image: { id: number }) => {
    try {
      const response = await imageService.getImageDetail({ image_id: image.id });
      if (response.status === 'success' && response.data) {
        setSelectedImage(response.data);
        setDrawerVisible(true);
      } else {
        message.error('获取图片详情失败');
      }
    } catch (error) {
      console.error('获取图片详情失败:', error);
      message.error('获取图片详情失败');
    }
  };

  const handleDelete = async (imageId: number) => {
    try {
      const response = await imageService.deleteImage({ image_id: imageId });
      if (response.status === 'success') {
        message.success('删除成功');
        setDrawerVisible(false);
        setRecentImages((prev) => prev.filter((img) => img.id !== imageId));
      }
    } catch (error) {
      console.error('删除失败:', error);
      message.error('删除失败');
    }
  };

  return (
    <div className="space-y-8">
      {/* 欢迎区 + 快捷动作 */}
      <section className="flex flex-col gap-5 rounded-xl border bg-card p-6 sm:flex-row sm:items-center sm:justify-between sm:p-8">
        <div className="space-y-1.5">
          <h1 className="font-serif text-2xl font-semibold tracking-tight text-foreground sm:text-3xl">
            你的图片收藏
          </h1>
          <p className="text-sm text-muted-foreground">
            {systemStats.totalImages > 0
              ? `共收录 ${systemStats.totalImages} 张图片 · ${systemStats.totalTags} 个标签，支持关键词与以图搜图`
              : '上传图片，用自然语言或相似图片快速找到它们'}
          </p>
        </div>
        <div className="flex shrink-0 flex-wrap gap-3">
          <Button onClick={() => navigate('/upload')} className="gap-2">
            <UploadCloud className="h-4 w-4" strokeWidth={2} />
            上传图片
          </Button>
          <Button variant="outline" onClick={() => navigate('/search')} className="gap-2">
            <ScanSearch className="h-4 w-4" strokeWidth={2} />
            以图搜图
          </Button>
        </div>
      </section>

      {/* 最近上传（画廊网格） */}
      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
            <ImagesIcon className="h-[18px] w-[18px] text-primary" strokeWidth={1.9} />
            最近上传
          </h2>
          <button
            type="button"
            onClick={() => navigate('/images')}
            className="flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-primary"
          >
            查看全部
            <ArrowRight className="h-4 w-4" strokeWidth={2} />
          </button>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="aspect-[4/3] animate-pulse rounded-lg bg-muted" />
            ))}
          </div>
        ) : recentImages.length > 0 ? (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
            {recentImages.map((image) => (
              <GalleryImageCard
                key={image.id}
                image={image as never}
                onClick={handleImageClick}
              />
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed py-20 text-center">
            <ImagesIcon className="h-10 w-10 text-muted-foreground/50" strokeWidth={1.5} />
            <p className="text-sm text-muted-foreground">还没有图片，先上传几张吧</p>
            <Button variant="outline" onClick={() => navigate('/upload')} className="gap-2">
              <UploadCloud className="h-4 w-4" strokeWidth={2} />
              去上传
            </Button>
          </div>
        )}
      </section>

      {/* 热门标签（柔和胶囊） */}
      {popularTags.length > 0 && (
        <section>
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-foreground">
            <TagsIcon className="h-[18px] w-[18px] text-primary" strokeWidth={1.9} />
            热门标签
          </h2>
          <div className="flex flex-wrap gap-2">
            {popularTags.slice(0, 20).map((tag) => (
              <button
                key={tag.tag}
                type="button"
                title={`${tag.count} 张图片使用此标签`}
                onClick={() => navigate(`/images?tags=${encodeURIComponent(tag.tag)}`)}
                className="rounded-full border bg-card px-3.5 py-1.5 text-sm text-secondary-foreground transition-colors hover:border-primary/40 hover:bg-accent hover:text-accent-foreground"
              >
                {tag.tag}
                <span className="ml-1.5 text-xs text-muted-foreground">{tag.count}</span>
              </button>
            ))}
          </div>
        </section>
      )}

      {/* 图片详情抽屉 */}
      <Drawer
        title="图片详情"
        placement="right"
        width={typeof window !== 'undefined' && window.innerWidth > 768 ? 600 : '100%'}
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        className="image-detail-drawer"
      >
        {selectedImage && (
          <SharedImageDetail
            image={selectedImage}
            onUpdate={setSelectedImage}
            onDelete={handleDelete}
            onClose={() => setDrawerVisible(false)}
          />
        )}
      </Drawer>
    </div>
  );
};

export default HomePage;
