/**
 * 首页组件所需的类型定义
 */
import { ImageDetail, TagInfo } from '@/types/models';
import { SystemStatusData } from '@/types/system';
import { SystemStatus } from '@/hooks/useSystemStatus';

/**
 * 系统统计数据
 */
export interface SystemStats {
  totalImages: number;
  status: string;
  totalTags: number;
}

/**
 * 状态卡片属性
 */
export interface StatusCardsProps {
  stats: SystemStats;
}

/**
 * 系统详情组件属性
 */
export interface SystemDetailsProps {
  systemStatus: SystemStatusData | null;
}

/**
 * 最近图片组件属性
 */
export interface RecentImagesProps {
  images: ImageDetail[];
}

/**
 * 热门标签组件属性
 */
export interface PopularTagsProps {
  tags: TagInfo[];
}

/**
 * 主标题栏组件属性
 */
export interface MainHeaderProps {
  collapsed: boolean;
  toggleCollapse: () => void;
  systemStatus: SystemStatus;
}

/**
 * 侧边栏菜单属性
 */
export interface SideMenuProps {
  collapsed: boolean;
}
