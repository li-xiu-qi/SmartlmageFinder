/**
 * 格式化日期字符串为本地日期时间格式
 * @param dateString ISO日期字符串
 * @returns 格式化后的日期字符串
 */
export const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch (error) {
    return dateString;
  }
};

/**
 * 格式化文件大小为可读格式
 * @param bytes 文件字节大小
 * @returns 格式化后的文件大小字符串
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  const size = (bytes / Math.pow(1024, i)).toFixed(2);
  
  return `${size} ${units[i]}`;
};

/**
 * 截断文本，超过指定长度时添加省略号
 * @param text 原始文本
 * @param length 最大长度
 * @returns 截断后的文本
 */
export const truncateText = (text: string, length = 100): string => {
  if (!text || text.length <= length) return text;
  return `${text.substring(0, length)}...`;
};

/**
 * 格式化标签数组为字符串
 * @param tags 标签数组
 * @returns 格式化后的标签字符串
 */
export const formatTags = (tags: string[]): string => {
  if (!tags || tags.length === 0) return '';
  return tags.join(', ');
};

/**
 * 图片路径转换为可访问的URL
 * 将后端存储的文件路径转换为前端可访问的URL
 * 例如: ./data/images/2023/04/30/123.jpg -> http://localhost:1000/static/images/2023/04/30/123.jpg
 * 或者: /images/2023/04/30/123.jpg -> http://localhost:1000/static/images/2023/04/30/123.jpg
 */
export const getImageUrl = (filepath: string): string => {
  if (!filepath) return '';

  // 如果已经是完整URL，则直接返回
  if (filepath.startsWith('http://') || filepath.startsWith('https://')) {
    return filepath;
  }

  // 如果是模拟数据中的图片URL (当使用mockData时)
  if (filepath.includes('picsum.photos')) {
    return filepath;
  }

  // 后端服务地址
  const API_BASE_URL = 'http://localhost:1000';

  // 处理包含 ./data/images 前缀的路径
  if (filepath.includes('./data/images/')) {
    const relativePath = filepath.replace('./data/images/', '');
    return `${API_BASE_URL}/static/images/${relativePath}`;
  }

  // 从路径中移除开头的 /images/，因为我们已经在静态路径中包含了images目录
  const normalizedPath = filepath.startsWith('/images/') 
    ? filepath.replace('/images/', '/') 
    : filepath;

  // 构建完整的静态资源URL（添加后端地址）
  return `${API_BASE_URL}/static/images${normalizedPath}`;
};

/**
 * 格式化日期时间
 * @param dateString ISO格式的日期字符串
 * @returns 格式化后的日期时间字符串 (YYYY-MM-DD HH:MM)
 */
export const formatDateTime = (dateString: string): string => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  return `${year}-${month}-${day} ${hours}:${minutes}`;
};