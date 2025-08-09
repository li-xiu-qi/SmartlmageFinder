import React, { useState, useEffect } from 'react';
import { Spin } from 'antd';

// 导入类型定义
import { ImageModel, TagInfo } from '@/types/models';
import { SystemStats } from './types';

// 导入服务
import imageService from '@/services/imageService';
import tagService from '@/services/tagService';
import systemService from '@/services/systemService';

// 导入子组件
import StatusCards from './components/home_detail/StatusCards';
import RecentImages from './components/home_detail/RecentImages';
import PopularTags from './components/home_detail/PopularTags';

// 引入样式
import './index.less';

/**
 * SmartImageFinder 首页组件
 * 展示系统概览、最近上传图片和热门标签
 */
const HomePage: React.FC = () => {  // 状态定义
  const [loading, setLoading] = useState(true);
  const [recentImages, setRecentImages] = useState<ImageModel[]>([]);
  const [popularTags, setPopularTags] = useState<TagInfo[]>([]);
  const [systemStats, setSystemStats] = useState<SystemStats>({
    totalImages: 0,
    status: 'unknown',
    totalTags: 0,
  });

  // 获取首页所需数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
          // 并行请求数据
        const [imagesResponse, tagsResponse, infoResponse, databaseResponse, storageResponse, cacheResponse] = await Promise.all([
          imageService.getImagesList({ 
            page: 1, 
            page_size: 8, 
            sort_by: 'created_at', 
            order: 'desc' 
          }),
          tagService.getPopularTags({ limit: 20 }),
          systemService.getSystemInfo(),
          systemService.getDatabaseInfo(),
          systemService.getStorageInfo(),
          systemService.getCacheInfo(),
        ]);

        // 处理图片数据
        if (imagesResponse.status === 'success' && imagesResponse.data) {
          setRecentImages(imagesResponse.data);
        }

        // 处理标签数据
        if (tagsResponse.status === 'success' && tagsResponse.data) {
          setPopularTags(tagsResponse.data);
        }        // 处理系统状态数据 - 提取需要的信息
        if (infoResponse.status === 'success' && 
            storageResponse.status === 'success' && 
            databaseResponse.status === 'success' && 
            cacheResponse.status === 'success') {
          
          // 更新系统统计数据
          setSystemStats({
            totalImages: storageResponse.data.total_images,
            status: infoResponse.data.status,
            totalTags: storageResponse.data.total_tags,
          });} else {
          // 如果获取系统状态失败，设置错误状态
          setSystemStats(prev => ({
            ...prev,
            status: 'error',
          }));
        }
      } catch (error) {
        console.error('获取首页数据失败:', error);
        // 设置所有统计数据为错误/初始状态
        setSystemStats({
          totalImages: 0,
          status: 'error',
          totalTags: 0,
        });
        setRecentImages([]);
        setPopularTags([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);
  return (
    <div className="home-page">
      <Spin spinning={loading}>
        {/* 状态卡片 */}
        <StatusCards stats={systemStats} />

        {/* 最近上传图片 */}
        <div className="recent-images">
          <RecentImages images={recentImages} />
        </div>

        {/* 热门标签 */}
        <div className="hot-tags">
          <PopularTags tags={popularTags} />
        </div>
      </Spin>
    </div>
  );
};

export default HomePage;