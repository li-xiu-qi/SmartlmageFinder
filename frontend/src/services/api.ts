/**
 * 服务导出文件
 * 
 * 集中导出所有服务，方便在组件中一次性导入多个服务
 */

import aiService from './aiService';
import imageService from './imageService';
import searchService from './searchService';
import systemService from './systemService';
import tagService from './tagService';

export {
  aiService,
  imageService,
  searchService,
  systemService,
  tagService
};
