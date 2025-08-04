// 导入 Ant Design 的 UploadFile 类型，用于文件上传列表项
import { UploadFile as AntUploadFile, RcFile } from 'antd/es/upload/interface';
// 导入项目中定义的图片数据模型
import { ImageModel } from '@/types/models';

// 扩展 Ant Design 的 UploadFile 类型，确保 originFileObj 存在且为 File 类型
// antd 的 UploadFile 类型中 originFileObj 是可选的，这里我们强制它存在，因为后续操作会依赖它
export interface UploadFile<T = unknown> extends AntUploadFile<T> {
  originFileObj: RcFile; // 原始的 File 对象，用于文件操作和上传, antd 使用 RcFile 类型
}

// 图片元数据结构，用于表单编辑和AI分析结果
// 这个接口定义了用户可以为图片编辑或AI可以生成的元数据字段
export interface ImageMetadata {
  title: string;         // 图片标题
  description: string;   // 图片描述
  tags: string[];        // 图片标签列表
  location?: string;      // 地点信息 (可选)
  event?: string;         // 事件信息 (可选)
  // 可以根据需要添加其他自定义元数据字段
}

// 单个文件上传结果
// 定义了处理单个文件上传后，该文件的状态和相关信息
export interface UploadResultItem {
  id: string;             // 对应 UploadFile 的 uid，用于关联前端列表中的文件项
  fileName: string;       // 上传的文件名
  success: boolean;       // 上传是否成功
  message?: string;        // 上传结果的消息，成功或失败原因
  image?: ImageModel;      // 如果上传成功，这里会包含后端返回的图片信息
  error?: Error | Record<string, unknown>; // 如果上传失败，这里会包含错误详情
}

// 批量上传总体结果
// 定义了批量上传操作完成后的整体统计信息
export interface UploadResult {
  items: UploadResultItem[]; // 每个文件的上传结果列表
  overallStatus: 'success' | 'partial' | 'failure'; // 整体上传状态：全部成功、部分成功、全部失败
  successCount: number;      // 成功上传的文件数量
  failureCount: number;      // 失败上传的文件数量
}

// 图片分析服务的配置 (如果需要在此处引用)
// import { ImageAnalysisServiceConfig } from '@/types/imageAnalysis';
// export type { ImageAnalysisServiceConfig };

// 可用标签的格式，用于下拉选择
// 定义了在标签选择器中展示的标签对象的结构
export interface SelectableTag {
  label: string; // 标签显示文本
  value: string; // 标签实际值
}

// 批量分析模式枚举
export enum AnalysisMode {
  ALL = 'all',              // 分析所有图片
  UNANALYZED_ONLY = 'unanalyzed_only' // 仅分析未分析的图片
}
