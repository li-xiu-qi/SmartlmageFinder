import React, { useState, useEffect } from 'react';
import { Tabs, message } from 'antd';
import { SearchOutlined, PictureOutlined, FontSizeOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import searchService from '@/services/searchService';
import tagService from '@/services/tagService';
import { ImageSearchResult, TagInfo } from '@/types/models';
import { UnifiedTextSearchParams, UnifiedImageSearchParams, FuzzySearchParams } from '@/types/search';
import TextSearchForm from './TextSearchForm';
import FuzzySearchForm from './FuzzySearchForm.tsx';
import ImageSearchForm from './ImageSearchForm';
import SearchResults from './SearchResults';
import { formatTagsForParam } from './utils';
import './styles.less';

/**
 * 搜索页面组件
 */
const SearchPage: React.FC = () => {  
  const [searchParams, setSearchParams] = useSearchParams();
  
  // 状态管理
  const [activeTab, setActiveTab] = useState<string>('text');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ImageSearchResult[]>([]);
  const [tags, setTags] = useState<TagInfo[]>([]);
  const [total, setTotal] = useState(0);
  const [searchTime, setSearchTime] = useState<number>(0);
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  const [referenceImage, setReferenceImage] = useState<{id: number, title: string} | undefined>(undefined);

  // 初始化 - 加载热门标签
  useEffect(() => {
    const loadTags = async () => {
      try {
        const response = await tagService.getPopularTags({ limit: 100 });
        if (response.status === 'success' && response.data) {
          setTags(response.data);
        }
      } catch (error) {
        console.error('Failed to load tags', error);
        message.error('加载标签失败');
      }
    };

    loadTags();
    
    // 从URL参数初始化标签
    const query = searchParams.get('q');
    if (query) {
      setSearchKeyword(query);
    }
    
    // 检查搜索参数中是否有tab参数，如果有则切换到对应的tab
    const tab = searchParams.get('tab');
  if (tab && (tab === 'text' || tab === 'image' || tab === 'fuzzy')) {
      setActiveTab(tab);
    }
  }, [searchParams]);
  // 执行模糊搜索 (LIKE)
  const handleFuzzySearch = async (params: FuzzySearchParams) => {
    setLoading(true);
    setSearchKeyword(params.q);

    try {
      const response = await searchService.fuzzySearch(params);
      if (response.status === 'success' && response.data) {
        setResults(response.data);
        setTotal(response.metadata?.total_results || response.data.length);
        setSearchTime(response.metadata?.execution_time_ms || 0);
        setReferenceImage(undefined);

        updateSearchParams({
          q: params.q,
          fields: params.fields ? params.fields.join(',') : undefined,
          tags: params.tags ? formatTagsForParam(params.tags) : undefined,
          start_date: params.start_date,
            end_date: params.end_date,
          tab: 'fuzzy'
        });
      } else {
        message.error(response.message || '模糊搜索失败');
      }
    } catch (error: unknown) {
      console.error('Fuzzy search failed', error);
      message.error(error instanceof Error ? error.message : '模糊搜索过程中发生错误');
    } finally {
      setLoading(false);
    }
  };


  // 执行文本搜索
  const handleTextSearch = async (params: UnifiedTextSearchParams) => {
    setLoading(true);
    setSearchKeyword(params.q);
    
    try {
      const response = await searchService.unifiedTextSearch(params);
        if (response.status === 'success' && response.data) {
        setResults(response.data);
        setTotal(response.metadata?.total_results || response.data.length);
        setSearchTime(response.metadata?.execution_time_ms || 0);
        setReferenceImage(response.metadata?.reference_image);
        
        // 更新URL参数
        updateSearchParams({
          q: params.q,
          vector_targets: params.vector_targets?.join(','),
          tags: params.tags ? formatTagsForParam(params.tags) : undefined,
          start_date: params.start_date,
          end_date: params.end_date,
          tab: 'text'
        });
      } else {
        message.error(response.message || '搜索失败');
      }
    } catch (error: unknown) {
      console.error('Text search failed', error);
      message.error(error instanceof Error ? error.message : '搜索过程中发生错误');
    } finally {
      setLoading(false);
    }
  };

  // 执行图像搜索
  const handleImageSearch = async (params: UnifiedImageSearchParams) => {
    setLoading(true);
    setSearchKeyword('图像搜索');
    
    try {
      const response = await searchService.unifiedImageSearch(params);
        if (response.status === 'success' && response.data) {
        setResults(response.data);
        setTotal(response.metadata?.total_results || response.data.length);
        setSearchTime(response.metadata?.execution_time_ms || 0);
        setReferenceImage(response.metadata?.reference_image);
        
        // 更新URL参数 (仅包含部分参数，因为图片文件不能放在URL中)
        updateSearchParams({
          search_targets: params.search_targets?.join(','),
          tags: params.tags ? formatTagsForParam(params.tags) : undefined,
          start_date: params.start_date,
          end_date: params.end_date,
          tab: 'image'
        });
      } else {
        message.error(response.message || '图像搜索失败');
      }
    } catch (error: unknown) {
      console.error('Image search failed', error);
      message.error(error instanceof Error ? error.message : '图像搜索过程中发生错误');
    } finally {
      setLoading(false);
    }
  };
  
  // 更新URL搜索参数
  const updateSearchParams = (params: Record<string, string | number | undefined>) => {
    const newParams = new URLSearchParams();
    
    // 仅添加有值的参数
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        newParams.set(key, String(value));
      }
    });
    
    setSearchParams(newParams);
  };

  // 处理标签页切换
  const handleTabChange = (activeKey: string) => {
    setActiveTab(activeKey);
    
    // 更新URL参数中的tab
    const newParams = new URLSearchParams(searchParams);
    newParams.set('tab', activeKey);
    setSearchParams(newParams);
  };

  return (
    <div className="search-page-container">
      <Tabs
        activeKey={activeTab}
        onChange={handleTabChange}
        className="search-tabs"
        items={[
          {
            key: 'fuzzy',
            label: <span><FontSizeOutlined /> 模糊搜索</span>,
            children: (
              <FuzzySearchForm
                onSearch={handleFuzzySearch}
                loading={loading}
                tags={tags}
              />
            )
          },
          {
            key: 'text',
            label: <span><SearchOutlined /> 语义搜索</span>,
            children: (
              <TextSearchForm 
                onSearch={handleTextSearch} 
                loading={loading} 
                tags={tags} 
              />
            )
          },
          {
            key: 'image',
            label: <span><PictureOutlined /> 以图语义搜索</span>,
            children: (
              <ImageSearchForm 
                onSearch={handleImageSearch} 
                loading={loading} 
                tags={tags} 
              />
            )
          }
        ]}
      />        <SearchResults 
        loading={loading} 
        results={results} 
        total={total} 
        searchTime={searchTime}
        searchKeyword={searchKeyword}
        referenceImage={referenceImage}
      />
    </div>
  );
};

export default SearchPage;
