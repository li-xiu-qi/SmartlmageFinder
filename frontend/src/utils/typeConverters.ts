/**
 * 类型转换工具，帮助将API返回的类型转换为UI组件需要的类型
 */
import { 
  ImageModel, 
  TagInfo, 
  SearchImageItem,
  PaginationMetadata,
} from '@/types/models';

/**
 * ImageCard 组件中使用的图片类型
 */
export interface ImageCardModel {
  id: number;
  filename: string;
  filepath: string;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
  file_size: number;
  file_type: string;
  width: number;
  height: number;
  tags: string[];
  // 额外附加搜索相关信息
  score?: number;
  distance?: number;
}

/**
 * 将后端API返回的图片模型转换为前端显示所需的模型
 */
export function convertToImageCardModel(image: ImageModel | SearchImageItem): ImageCardModel {
  return {
    id: image.id,
    filename: image.filename,
    filepath: image.filepath,
    title: image.title || image.filename,
    description: image.description || '',
    created_at: image.created_at,
    updated_at: image.updated_at,
    file_size: image.file_size,
    file_type: image.file_type,
    width: image.width,
    height: image.height,
    tags: Array.isArray(image.tags) ? image.tags : [],
    // 如果是搜索结果，添加相关性得分
    ...(isSearchImageItem(image) && {
      score: image.score,
      distance: image.distance
    })
  };
}

/**
 * 类型守卫：判断是否为搜索图片项
 */
function isSearchImageItem(image: ImageModel | SearchImageItem): image is SearchImageItem {
  return 'score' in image || 'distance' in image;
}

/**
 * 将标签信息转换为Select组件选项格式
 */
export function convertTagsToOptions(tags: TagInfo[]) {
  return tags.map(tag => ({
    label: `${tag.tag} (${tag.count})`,
    value: tag.tag
  }));
}

/**
 * 分页参数转换
 */
export function createPaginationProps(pagination: PaginationMetadata) {
  return {
    current: pagination.page,
    pageSize: pagination.page_size,
    total: pagination.total_items,
    showSizeChanger: true,
    showQuickJumper: true,
    showTotal: (total: number) => `共 ${total} 张图片`
  };
}
