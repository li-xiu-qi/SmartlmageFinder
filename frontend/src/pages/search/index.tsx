import React, { useState, useEffect } from 'react';
import { message } from 'antd';
import { ScanSearch, Image as ImageIcon, Type } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';
import { cn } from '@/lib/utils';
import searchService from '@/services/searchService';
import tagService from '@/services/tagService';
import { useVectorCapability } from '@/hooks/useVectorCapability';
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

  // 向量能力检测
  const { vectorEnabled, status: vectorStatus } = useVectorCapability();

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

  // 向量不可用时自动切换到模糊搜索
  useEffect(() => {
    if (!vectorEnabled && (activeTab === 'text' || activeTab === 'image')) {
      setActiveTab('fuzzy');
    }
  }, [vectorEnabled, activeTab]);

  // 构建降级提示信息
  const unavailableReasons: string[] = [];
  if (vectorStatus && !vectorStatus.driver.available) {
    unavailableReasons.push('sqlite-vec 驱动未加载');
  }
  if (vectorStatus && !vectorStatus.model.available) {
    unavailableReasons.push('Embedding 模型未配置或未下载');
  }
  const degradeMessage = unavailableReasons.length > 0
    ? `语义搜索不可用（${unavailableReasons.join('、')}）。请使用「模糊搜索」进行关键词检索。`
    : '';

  const tabs = [
    { key: 'text', label: '语义搜索', icon: ScanSearch, enabled: vectorEnabled, node: <TextSearchForm onSearch={handleTextSearch} loading={loading} tags={tags} /> },
    { key: 'image', label: '以图搜图', icon: ImageIcon, enabled: vectorEnabled, node: <ImageSearchForm onSearch={handleImageSearch} loading={loading} tags={tags} /> },
    { key: 'fuzzy', label: '关键词搜索', icon: Type, enabled: true, node: <FuzzySearchForm onSearch={handleFuzzySearch} loading={loading} tags={tags} /> },
  ];

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="font-serif text-2xl font-semibold tracking-tight text-foreground">搜索图片</h1>
        <p className="text-sm text-muted-foreground">用自然语言描述、上传参考图，或按关键词检索你的收藏</p>
      </div>

      {!vectorEnabled && degradeMessage && (
        <div className="rounded-lg border border-amber-300/50 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          <span className="font-medium">语义搜索暂不可用。</span> {degradeMessage}
        </div>
      )}

      {/* 分段切换 */}
      <div className="inline-flex rounded-lg border bg-card p-1">
        {tabs.map(({ key, label, icon: Icon, enabled }) => (
          <button
            key={key}
            type="button"
            disabled={!enabled}
            onClick={() => enabled && handleTabChange(key)}
            className={cn(
              'flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors',
              activeTab === key
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground',
              !enabled && 'cursor-not-allowed opacity-40 hover:text-muted-foreground'
            )}
          >
            <Icon className="h-4 w-4" strokeWidth={1.9} />
            {label}
          </button>
        ))}
      </div>

      {/* 当前搜索表单 */}
      <div className="rounded-xl border bg-card p-5">
        {tabs.find((t) => t.key === activeTab)?.node}
      </div>

      <SearchResults
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
