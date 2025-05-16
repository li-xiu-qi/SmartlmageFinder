import apiClient from './apiClient';
import {
  SearchClient,
  TextSearchParams,
  TextSearchResponse,
  ImageSearchParams,
  ImageSearchResponse,
  SimilarSearchQueryParams,
  SimilarSearchResponse
} from '../types/search';
import { SearchImageItem } from '../types/models';

// 定义将发送给 Axios 进行 similarSearch 的参数类型，
// 其中 'tags' 是字符串，其他数组类型保留供 Axios 的默认序列化使用。
type AxiosSimilarSearchQueryInternalParams = Omit<SimilarSearchQueryParams, 'tags'> & {
  tags?: string; // 标签将是逗号分隔的字符串
};

const searchService: SearchClient = {
  // 文本搜索
  textSearch: (params: TextSearchParams): Promise<TextSearchResponse> => {
    return apiClient.getWithTransform<SearchImageItem[]>('/search/text', { params }) as Promise<TextSearchResponse>;
  },

  // 图像搜索
  imageSearch: (params: ImageSearchParams): Promise<ImageSearchResponse> => {
    const formData = new FormData();
    formData.append('file', params.file);

    if (params.search_targets && params.search_targets.length > 0) {
      params.search_targets.forEach(target => {
        formData.append('search_targets', target);
      });
    }
    if (params.search_type) {
      formData.append('search_type', params.search_type);
    }
    if (params.filename) {
      formData.append('filename', params.filename);
    }
    if (params.tags && params.tags.length > 0) {
      formData.append('tags', params.tags.join(','));
    }
    if (params.start_date) {
      formData.append('start_date', params.start_date);
    }
    if (params.end_date) {
      formData.append('end_date', params.end_date);
    }
    if (typeof params.limit === 'number') {
      formData.append('limit', params.limit.toString());
    }
    if (typeof params.offset === 'number') {
      formData.append('offset', params.offset.toString());
    }

    return apiClient.postWithTransform<SearchImageItem[]>('/search/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }) as Promise<ImageSearchResponse>;
  },

  // 相似图片搜索
  similarSearch: (imageId: number | string, queryParams?: SimilarSearchQueryParams): Promise<SimilarSearchResponse> => {
    let apiParams: AxiosSimilarSearchQueryInternalParams | undefined = undefined;

    if (queryParams) {
      const { tags, ...rest } = queryParams;
      apiParams = { ...rest }; // 首先展开其他属性

      if (tags && tags.length > 0) {
        apiParams.tags = tags.join(',');
      }
      // 如果处理后 apiParams 没有键，则将其设为 undefined，这样 axios 就不会发送查询字符串。
      if (Object.keys(apiParams).length === 0) {
        apiParams = undefined;
      }
    }

    return apiClient.getWithTransform<SearchImageItem[]>(
      `/search/similar/${imageId}`,
      { params: apiParams }
    ) as Promise<SimilarSearchResponse>;
  },
};

export default searchService;
