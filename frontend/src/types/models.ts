/**
 * SmartImageFinder 共享数据模型定义
 * 这个文件包含了多个模块共享的核心数据结构
 */

/**
 * 图片详细信息 (原 ImageModel)
 * 这是系统中最核心的图片数据结构，被多个模块共享使用
 */
export interface ImageDetail {
  id: number;                      // 图片ID
  filename: string;                // 文件名
  filepath: string;                // 文件路径
  title: string;                   // 图片标题
  description: string;             // 图片描述
  file_size: number;               // 文件大小(字节)
  file_type: string;               // 文件类型(MIME类型)
  width: number;                   // 图片宽度(像素)
  height: number;                  // 图片高度(像素)
  created_at: string;              // 创建时间(ISO格式)
  updated_at: string;              // 更新时间(ISO格式)
  tags: string[];                  // 标签列表
  metadata: Record<string, unknown>; // 元数据
}

/**
 * 分页元数据
 */
export interface PaginationMetadata {
  page: number;        // 当前页码
  page_size: number;   // 每页条目数 
  total_items: number; // 总条目数
  total_pages: number; // 总页数
}

/**
 * 标签信息（带使用计数）
 */
export interface TagInfo {
  tag: string;       // 标签名称
  count: number;     // 标签使用次数
}

/**
 * 搜索结果中的图片项 (原 SearchImageItem)
 * 扩展了基本的 ImageDetail，添加了搜索相关的字段
 */
export interface ImageSearchResult extends ImageDetail {
  score?: number;    // 文本搜索相关性得分（0-1之间）
  distance?: number; // 向量搜索距离（越小越相似）
}

/**
 * 删除图片后返回的数据结构
 */
export interface DeletedImageInfo {
  id: number;        // 图片ID
  filename: string;  // 文件名
}
