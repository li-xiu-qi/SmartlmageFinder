/**
 * 服务导出文件
 * 
 * 集中导出所有服务，方便在组件中一次性导入多个服务
 */

import imageAnalysisService from './imageAnalysisService';
import imageService from './imageService';
import searchService from './searchService';
import systemService from './systemService';
import tagService from './tagService';
import metadataService from './metadataService'; // 导入 metadataService

export {
  imageAnalysisService,
  imageService,
  searchService,
  systemService,
  tagService,
  metadataService // 导出 metadataService
};
