// 模拟数据，用于在后端API不可用时提供测试数据
import { Image, ImageDetail, Tag, SystemStatus } from '@/types';

// 模拟标签数据
export const mockTags: Tag[] = [
  { name: '风景', count: 32 },
  { name: '人物', count: 27 },
  { name: '建筑', count: 15 },
  { name: '动物', count: 12 },
  { name: '美食', count: 10 },
  { name: '日落', count: 8 },
  { name: '海滩', count: 7 },
  { name: '城市', count: 6 },
  { name: '植物', count: 5 },
  { name: '山脉', count: 4 },
];

// 生成模拟图片的随机标签
const getRandomTags = (): string[] => {
  const shuffled = [...mockTags].sort(() => 0.5 - Math.random());
  const count = Math.floor(Math.random() * 4) + 1; // 随机1-4个标签
  return shuffled.slice(0, count).map(tag => tag.name);
};

// 生成模拟图片的基本URL
const getImageUrl = (index: number): string => {
  // 使用占位图片服务
  return `https://picsum.photos/id/${(index % 30) + 1}/300/200`;
};

// 生成模拟图片数据
export const generateMockImages = (count: number = 20): Image[] => {
  return Array.from({ length: count }).map((_, index) => {
    const id = Math.floor(Math.random() * 10000000).toString();
    return {
      uuid: `img-${id}`,
      title: `测试图片 ${id}`,
      description: `这是一张测试图片，用于前端开发和测试目的`,
      filepath: getImageUrl(index),
      filename: `image_${id}.jpg`,
      file_size: Math.floor(Math.random() * 5000000) + 500000, // 0.5MB - 5.5MB
      file_type: 'jpg',
      width: 1920,
      height: 1080,
      created_at: new Date(Date.now() - Math.floor(Math.random() * 30 * 24 * 60 * 60 * 1000)).toISOString(),
      tags: getRandomTags(),
    };
  });
};

// 生成模拟图片详情
export const generateMockImageDetail = (uuid: string): ImageDetail => {
  const baseImage = generateMockImages(1)[0];
  baseImage.uuid = uuid;
  
  return {
    ...baseImage,
    updated_at: new Date().toISOString(),
    metadata: {
      '拍摄地点': '北京',
      '相机型号': 'Canon EOS R5',
      '拍摄时间': '2023-05-01 15:30:00',
      '光圈值': 'f/2.8',
      '曝光时间': '1/125s',
      'ISO': '400',
    }
  };
};

// 模拟系统状态
export const mockSystemStatus: SystemStatus = {
  system: {
    version: '1.0.0',
    uptime: 86400,
    status: 'healthy'
  },
  components: {
    model: {
      status: 'loaded',
      name: 'jina-clip-v2',
      load_time: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()
    },
    database: {
      status: 'connected',
      type: 'sqlite',
      version: '3.39.4'
    },
    multimodal_api: {
      status: 'available',
      model: 'Qwen2.5-VL-32B-Instruct'
    }
  },
  storage: {
    total_images: 156,
    total_size_mb: 1250
  }
};

// 生成搜索结果
export const generateMockSearchResults = (query: string, count: number = 10) => {
  const results = generateMockImages(count).map(image => ({
    ...image,
    score: Math.random() * 0.3 + 0.7 // 70%-100%的相似度分数
  }));
  
  // 按相似度排序
  results.sort((a, b) => b.score - a.score);
  
  return results;
};

// 生成模拟上传结果
export const generateMockUploadResult = (fileCount: number) => {
  const successCount = Math.min(fileCount, fileCount - Math.floor(Math.random() * 2));
  const failCount = fileCount - successCount;
  
  const uploaded = Array.from({ length: successCount }).map((_, index) => ({
    uuid: `upload-${Date.now()}-${index}`,
    original_filename: `image_${index + 1}.jpg`,
    file_size: Math.floor(Math.random() * 5000000) + 500000,
    stored_path: `/images/2023/05/${Date.now()}-${index}.jpg`
  }));
  
  const failed = Array.from({ length: failCount }).map((_, index) => ({
    filename: `failed_${index + 1}.tiff`,
    error: index % 2 === 0 ? '文件格式不支持' : '文件大小超过限制'
  }));
  
  return {
    uploaded,
    failed
  };
};