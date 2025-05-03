import React, { useState, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Row,
  Col,
  Tabs,
  Form,
  Upload,
  Select,
  DatePicker,
  Space,
  Radio,
  Divider,
  Empty,
  Spin,
  message,
  Slider,
  Badge,
  Switch,
  Tooltip,
  Tag as AntdTag
} from 'antd';
import {
  SearchOutlined,
  UploadOutlined,
  PictureOutlined,
  FilterOutlined,
  ReloadOutlined,
  LoadingOutlined,
  InboxOutlined,
  DeleteOutlined,
  InfoCircleOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import { useSearchParams, useNavigate } from 'react-router-dom';
import type { UploadFile, UploadProps } from 'antd';
import type { RcFile } from 'antd/es.upload';
import { searchService, tagService } from '@/services/api';
import { Tag as TagType, ImageSearchResult } from '@/types';
import ImageCard from '@/components/ImageCard';
import { debounce } from 'lodash';

const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { Dragger } = Upload;

// 定义搜索类型选项
const searchTypes = [
  { value: 'text', label: '文本匹配' },
  { value: 'vector', label: '向量搜索' },
  { value: 'hybrid', label: '混合搜索' }
];

// 定义文本匹配模式选项
const textMatchModes = [
  { value: 'title', label: '仅标题' },
  { value: 'description', label: '仅描述' },
  { value: 'combined', label: '标题+描述' }
];

// 定义向量匹配模式选项
const vectorMatchModes = [
  { value: 'title', label: '标题向量' },
  { value: 'description', label: '描述向量' },
  { value: 'combined', label: '标题+描述向量' }
];

// 定义图片向量匹配模式选项
const imageMatchModes = [
  { value: 'image', label: '图片向量' },
  { value: 'title', label: '标题向量' },
  { value: 'description', label: '描述向量' },
  { value: 'combined', label: '综合向量' }
];

const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  // 状态管理
  const [activeTab, setActiveTab] = useState<string>('text');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ImageSearchResult[]>([]);
  const [tags, setTags] = useState<TagType[]>([]);
  const [searchImage, setSearchImage] = useState<RcFile | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [total, setTotal] = useState(0);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [searchTime, setSearchTime] = useState<number>(0);
  const [selectedImageMatchModes, setSelectedImageMatchModes] = useState<string[]>(['image']); 
  const [modeWeights, setModeWeights] = useState<{[key: string]: number}>({ 
    image: 1.0 
  });

  // 使用 Form.useWatch 监听表单值变化
  const watchSearchType = Form.useWatch('search_type', form);
  const watchTextMatchMode = Form.useWatch('text_match_mode', form);
  const watchVectorMatchMode = Form.useWatch('vector_match_mode', form);
  const watchImageSearchType = Form.useWatch('image_search_type', form);
  
  // 当图片搜索类型发生变化时，更新匹配模式
  useEffect(() => {
    if (watchImageSearchType && watchImageSearchType !== 'combined') {
      // 如果选择了特定的搜索类型（而非综合类型），则将匹配模式设置为该类型
      setSelectedImageMatchModes([watchImageSearchType]);
      setModeWeights({ [watchImageSearchType]: 1.0 });
    } else if (watchImageSearchType === 'combined') {
      // 如果选择了综合类型，则使用多种匹配模式
      const newSelectedModes = ['image', 'title', 'description'];
      setSelectedImageMatchModes(newSelectedModes);
      
      // 均等分配权重
      const weight = 1.0 / newSelectedModes.length;
      const newWeights: {[key: string]: number} = {};
      newSelectedModes.forEach(mode => {
        newWeights[mode] = weight;
      });
      setModeWeights(newWeights);
    }
  }, [watchImageSearchType]);

  // 初始化表单值
  useEffect(() => {
    const query = searchParams.get('q');
    const searchType = searchParams.get('search_type') || 'hybrid';
    const textMatchMode = searchParams.get('text_match_mode') || 'combined';
    const vectorMatchMode = searchParams.get('vector_match_mode') || 'combined';
    const tagsParam = searchParams.get('tags');
    
    // 如果URL中有查询参数，设置表单值
    if (query) {
      form.setFieldsValue({ query });
      // 执行搜索
      handleTextSearch({ 
        query, 
        search_type: searchType, 
        text_match_mode: textMatchMode,
        vector_match_mode: vectorMatchMode
      });
    }
    
    if (tagsParam) {
      const tagsArray = tagsParam.split(',').map(tag => tag.trim());
      form.setFieldsValue({ tags: tagsArray });
    }
    
    // 设置搜索类型和匹配模式
    form.setFieldsValue({ 
      search_type: searchType,
      text_match_mode: textMatchMode,
      vector_match_mode: vectorMatchMode
    });
  }, []);

  // 获取标签数据
  useEffect(() => {
    const fetchTags = async () => {
      try {
        const response = await tagService.getTags();
        if (response.status === 'success' && response.data) {
          setTags(response.data.tags || []);
        }
      } catch (error) {
        console.error('获取标签失败:', error);
      }
    };

    fetchTags();
  }, []);

  // 格式化权重为逗号分隔的字符串
  const formatWeights = (weights: {[key: string]: number}, modes: string[]): string => {
    return modes.map(mode => weights[mode] || 0).join(',');
  };

  // 执行文本搜索
  const handleTextSearch = async (values: any) => {
    try {
      const { query, search_type, text_match_mode, vector_match_mode, tags, date_range } = values;
      
      if (!query || query.trim() === '') {
        message.warning('请输入搜索关键词');
        return;
      }
      
      setLoading(true);
      
      // 构建搜索参数
      const searchParams: any = {
        q: query,
        search_type: search_type || 'hybrid',
        text_match_mode: text_match_mode || 'combined',
        vector_match_mode: vector_match_mode || 'combined',
        limit: 50,
      };
      
      // 添加标签过滤
      if (tags && tags.length > 0) {
        searchParams.tags = tags.join(',');
      }
      
      // 添加日期范围过滤
      if (date_range && date_range.length === 2) {
        searchParams.start_date = date_range[0].format('YYYY-MM-DD');
        searchParams.end_date = date_range[1].format('YYYY-MM-DD');
      }
      
      // 更新URL参数
      setSearchParams({ 
        q: query,
        search_type: searchParams.search_type,
        text_match_mode: searchParams.text_match_mode,
        vector_match_mode: searchParams.vector_match_mode,
        ...(searchParams.tags ? { tags: searchParams.tags } : {})
      });
      
      // 调用搜索API
      const response = await searchService.searchByText(searchParams);
      
      if (response.status === 'success' && response.data) {
        setResults(response.data.results || []);
        setTotal(response.data.results.length);
        
        // 设置搜索时间（如果存在）
        if (response.metadata?.time_ms) {
          setSearchTime(response.metadata.time_ms);
        }
      }
    } catch (error) {
      console.error('搜索失败:', error);
      message.error('搜索失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 处理文件上传前的检查
  const beforeImageUpload = (file: RcFile) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('只能上传图片文件!');
      return false;
    }
    
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('图片大小不能超过10MB!');
      return false;
    }
    
    // 这里设置为false阻止默认上传行为，我们将手动处理上传
    return false;
  };

  // 处理文件列表变化
  const handleFileChange = (info: any) => {
    // info.fileList是文件列表，这里我们只处理单个文件
    const { file, fileList } = info;
    
    if (!file) return;
    
    // 更新文件列表状态，控制UI显示
    setFileList(fileList.slice(-1));
    
    if (file.status !== 'removed') {
      // 检查文件类型
      if (!file.type || !file.type.startsWith('image/')) {
        message.error('只能上传图片文件!');
        return;
      }
  
      // 检查文件大小
      if (file.size && file.size / 1024 / 1024 > 10) {
        message.error('图片大小不能超过10MB!');
        return;
      }
  
      // 保存文件对象 - 同时处理两种可能的文件对象格式
      const fileObj = file.originFileObj || file;
      if (fileObj) {
        setSearchImage(fileObj as RcFile);
        console.log('设置搜索图片:', fileObj);
        
        // 生成预览图
        const reader = new FileReader();
        reader.readAsDataURL(fileObj);
        reader.onload = () => {
          setImageUrl(reader.result as string);
        };
      }
    }
  };

  // 移除图片
  const handleImageRemove = () => {
    setSearchImage(null);
    setImageUrl('');
    setFileList([]);
    return true;
  };

  // 执行图片搜索
  const handleImageSearch = async () => {
    try {
      if (!searchImage) {
        message.warning('请先上传图片');
        return;
      }
      
      const values = form.getFieldsValue();
      setLoading(true);
      
      // 构建搜索参数
      const formData = new FormData();
      formData.append('image', searchImage);
      formData.append('search_type', values.image_search_type || 'image');
      
      // 添加匹配模式
      if (selectedImageMatchModes.length > 0) {
        // 在formData中需要为每个匹配模式添加一个条目
        selectedImageMatchModes.forEach(mode => {
          formData.append('match_modes', mode);
        });
        
        // 添加权重
        if (Object.keys(modeWeights).length > 0) {
          const weightString = formatWeights(modeWeights, selectedImageMatchModes);
          formData.append('weights', weightString);
        }
      }
      
      // 添加结果限制
      formData.append('limit', '50');
      
      // 添加标签过滤
      if (values.tags && values.tags.length > 0) {
        formData.append('tags', values.tags.join(','));
      }
      
      // 添加日期范围过滤
      if (values.date_range && values.date_range.length === 2) {
        formData.append('start_date', values.date_range[0].format('YYYY-MM-DD'));
        formData.append('end_date', values.date_range[1].format('YYYY-MM-DD'));
      }
      
      // 调用图片搜索API
      const response = await searchService.searchByImage(formData);
      
      if (response.status === 'success' && response.data) {
        setResults(response.data.results || []);
        setTotal(response.data.results.length);
        
        // 设置搜索时间（如果存在）
        if (response.metadata?.time_ms) {
          setSearchTime(response.metadata.time_ms);
        }
      }
    } catch (error) {
      console.error('图片搜索失败:', error);
      message.error('图片搜索失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 处理匹配模式变化
  const handleMatchModesChange = (selectedModes: string[]) => {
    // 不允许空选项
    if (selectedModes.length === 0) {
      message.warning('至少需要选择一种匹配模式');
      return;
    }
    
    setSelectedImageMatchModes(selectedModes);
    
    // 重新初始化权重
    const defaultWeight = 1.0 / selectedModes.length;
    const newWeights: {[key: string]: number} = {};
    
    selectedModes.forEach(mode => {
      newWeights[mode] = defaultWeight;
    });
    
    setModeWeights(newWeights);
  };

  // 更新特定匹配模式的权重
  const updateModeWeight = (mode: string, weight: number) => {
    const newWeights = { ...modeWeights, [mode]: weight };
    
    // 确保权重总和为1
    const sum = Object.values(newWeights).reduce((a, b) => a + b, 0);
    
    // 如果总和不是1，调整其他权重
    if (sum !== 1 && selectedImageMatchModes.length > 1) {
      const otherModesCount = selectedImageMatchModes.length - 1;
      const remainingWeight = 1.0 - weight;
      
      if (remainingWeight <= 0) {
        message.warning('权重无效，其他匹配模式需要有权重');
        return;
      }
      
      const weightPerOtherMode = remainingWeight / otherModesCount;
      
      selectedImageMatchModes.forEach(m => {
        if (m !== mode) {
          newWeights[m] = weightPerOtherMode;
        }
      });
    }
    
    setModeWeights(newWeights);
  };

  // 切换高级选项显示
  const toggleAdvanced = () => {
    setShowAdvanced(!showAdvanced);
  };

  // 切换搜索模式选项卡
  const handleTabChange = (key: string) => {
    setActiveTab(key);
    setResults([]);
  };

  // 渲染文本搜索面板
  const renderTextSearch = () => (
    <div className="text-search-panel">
      <Form 
        form={form}
        onFinish={handleTextSearch}
        initialValues={{
          search_type: 'hybrid',
          text_match_mode: 'combined',
          vector_match_mode: 'combined',
        }}
      >
        <Form.Item name="query">
          <Input
            placeholder="输入关键词搜索图片..."
            prefix={<SearchOutlined />}
            size="large"
            allowClear
            onPressEnter={() => form.submit()}
          />
        </Form.Item>

        {/* 添加简要搜索模式显示 - 使用监听的表单值 */}
        <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <Space size="small">
              <span style={{ color: '#666' }}>当前模式:</span>
              <AntdTag color="blue">
                {searchTypes.find(t => t.value === watchSearchType)?.label || '混合搜索'}
              </AntdTag>
              <AntdTag color="cyan">
                {textMatchModes.find(m => m.value === watchTextMatchMode)?.label || '标题+描述'}
              </AntdTag>
              {watchSearchType !== 'text' && (
                <AntdTag color="green">
                  {vectorMatchModes.find(m => m.value === watchVectorMatchMode)?.label || '标题+描述向量'}
                </AntdTag>
              )}
            </Space>
          </div>
          <Button type="link" onClick={toggleAdvanced}>
            {showAdvanced ? '收起高级选项' : '显示高级选项'}
          </Button>
        </div>

        {showAdvanced && (
          <div className="advanced-options">
            <Row gutter={16}>
              <Col xs={24} md={8}>
                <Form.Item 
                  name="search_type" 
                  label={
                    <span>
                      搜索类型
                      <Tooltip title="选择使用传统文本匹配、向量搜索或两者结合">
                        <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                      </Tooltip>
                    </span>
                  }
                >
                  <Select>
                    {searchTypes.map(type => (
                      <Option key={type.value} value={type.value}>{type.label}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              
              <Col xs={24} md={8}>
                <Form.Item 
                  name="text_match_mode" 
                  label={
                    <span>
                      文本匹配模式
                      <Tooltip title="选择是仅匹配标题、仅匹配描述还是两者都匹配">
                        <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                      </Tooltip>
                    </span>
                  }
                >
                  <Select>
                    {textMatchModes.map(mode => (
                      <Option key={mode.value} value={mode.value}>{mode.label}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              
              <Col xs={24} md={8}>
                <Form.Item 
                  name="vector_match_mode" 
                  label={
                    <span>
                      向量匹配模式
                      <Tooltip title="选择使用标题向量、描述向量还是二者结合的向量进行搜索">
                        <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                      </Tooltip>
                    </span>
                  }
                >
                  <Select>
                    {vectorMatchModes.map(mode => (
                      <Option key={mode.value} value={mode.value}>{mode.label}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>

            <Form.Item name="date_range" label="日期范围">
              <RangePicker style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item name="tags" label="标签过滤">
              <Select
                mode="multiple"
                placeholder="选择标签过滤搜索结果"
                style={{ width: '100%' }}
                allowClear
              >
                {tags.map(tag => (
                  <Option key={tag.name} value={tag.name}>
                    {tag.name} ({tag.count})
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </div>
        )}

        <Form.Item>
          <Button type="primary" icon={<SearchOutlined />} htmlType="submit" loading={loading} block>
            搜索
          </Button>
        </Form.Item>
      </Form>
    </div>
  );

  // 渲染图片搜索面板
  const renderImageSearch = () => (
    <div className="image-search-panel">
      <Form form={form} initialValues={{ image_search_type: 'image' }}>
        <div className="upload-wrapper" style={{ marginBottom: 16 }}>
          <Dragger
            name="image"
            fileList={fileList}
            multiple={false}
            showUploadList={true}
            beforeUpload={beforeImageUpload}
            onChange={handleFileChange}
            onRemove={handleImageRemove}
            listType="picture-card"
            accept="image/*"
            style={{ marginBottom: 16 }}
          >
            {imageUrl ? (
              <img src={imageUrl} alt="搜索图片" style={{ maxHeight: 200, maxWidth: '100%' }} />
            ) : (
              <>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽图片到此区域</p>
                <p className="ant-upload-hint">
                  上传图片以搜索相似的图片，支持JPG、PNG等格式
                </p>
              </>
            )}
          </Dragger>
        </div>

        {/* 添加简要搜索模式显示 - 使用监听的表单值和状态 */}
        <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <Space size="small">
              <span style={{ color: '#666' }}>当前模式:</span>
              <AntdTag color="purple">
                {imageMatchModes.find(m => m.value === watchImageSearchType)?.label || '图片向量'}
              </AntdTag>
              {selectedImageMatchModes.length > 0 && (
                <AntdTag color="magenta">
                  匹配: {selectedImageMatchModes.map(mode => 
                    imageMatchModes.find(m => m.value === mode)?.label
                  ).join('+')}
                </AntdTag>
              )}
              {selectedImageMatchModes.length > 1 && (
                <Tooltip title="多模式权重可在高级选项中设置">
                  <InfoCircleOutlined style={{ color: '#1890ff' }} />
                </Tooltip>
              )}
            </Space>
          </div>
          <Button type="link" onClick={toggleAdvanced}>
            {showAdvanced ? '收起高级选项' : '显示高级选项'}
          </Button>
        </div>

        {showAdvanced && (
          <div className="advanced-options">
            <Form.Item 
              name="image_search_type" 
              label={
                <span>
                  搜索类型
                  <Tooltip title="选择使用图像向量、标题向量、描述向量还是综合向量进行搜索">
                    <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                  </Tooltip>
                </span>
              }
            >
              <Select>
                {imageMatchModes.map(mode => (
                  <Option key={mode.value} value={mode.value}>{mode.label}</Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item 
              label={
                <span>
                  匹配模式组合
                  <Tooltip title="选择多种匹配模式并设置权重，结果将根据组合得分排序">
                    <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                  </Tooltip>
                </span>
              }
            >
              <Select
                mode="multiple"
                placeholder="选择匹配模式组合"
                style={{ width: '100%' }}
                value={selectedImageMatchModes}
                onChange={handleMatchModesChange}
              >
                {imageMatchModes.map(mode => (
                  <Option key={mode.value} value={mode.value}>{mode.label}</Option>
                ))}
              </Select>
            </Form.Item>

            {selectedImageMatchModes.length > 1 && (
              <div className="weights-sliders">
                <Divider orientation="left">匹配模式权重设置</Divider>
                {selectedImageMatchModes.map(mode => (
                  <Form.Item 
                    key={mode} 
                    label={
                      <span>
                        {imageMatchModes.find(m => m.value === mode)?.label || mode} 权重
                        <AntdTag color="blue" style={{ marginLeft: 8 }}>
                          {modeWeights[mode]?.toFixed(2) || 0}
                        </AntdTag>
                      </span>
                    }
                  >
                    <Slider
                      min={0.01}
                      max={1}
                      step={0.01}
                      value={modeWeights[mode] || 0}
                      onChange={(value) => updateModeWeight(mode, value)}
                      tooltip={{ formatter: (value) => value?.toFixed(2) }}
                    />
                  </Form.Item>
                ))}
              </div>
            )}

            <Form.Item name="date_range" label="日期范围">
              <RangePicker style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item name="tags" label="标签过滤">
              <Select
                mode="multiple"
                placeholder="选择标签过滤搜索结果"
                style={{ width: '100%' }}
                allowClear
              >
                {tags.map(tag => (
                  <Option key={tag.name} value={tag.name}>
                    {tag.name} ({tag.count})
                  </Option>
                ))}
              </Select>
            </Form.Item>
          </div>
        )}

        <Button 
          type="primary" 
          icon={<SearchOutlined />} 
          onClick={handleImageSearch}
          disabled={!searchImage}
          loading={loading}
          block
        >
          以图搜图
        </Button>
      </Form>
    </div>
  );

  // 渲染搜索结果
  const renderSearchResults = () => {
    if (loading) {
      return (
        <div style={{ textAlign: 'center', padding: '40px 0' }}>
          <Spin size="large" />
          <p style={{ marginTop: 16 }}>正在搜索中，请稍候...</p>
        </div>
      );
    }

    if (results.length === 0) {
      return (
        <Empty 
          description="暂无搜索结果" 
          image={Empty.PRESENTED_IMAGE_SIMPLE} 
        />
      );
    }

    return (
      <div className="search-results">
        <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
          <div>
            共找到 <strong>{total}</strong> 个结果
          </div>
          {searchTime > 0 && (
            <div>
              搜索用时: <strong>{searchTime}</strong> 毫秒
            </div>
          )}
        </div>
        
        <Row gutter={[16, 16]}>
          {results.map(image => (
            <Col xs={12} sm={8} md={6} lg={4} xl={4} key={image.uuid}>
              <ImageCard 
                image={image} 
                showSimilarity={true}
                showTags={true}
                onClick={(img) => navigate(`/images/${img.uuid}`)} 
              />
            </Col>
          ))}
        </Row>
      </div>
    );
  };

  return (
    <div className="search-page">
      <Card>
        <Tabs 
          activeKey={activeTab} 
          onChange={handleTabChange}
          type="card"
          tabBarStyle={{ marginBottom: 24 }}
        >
          <TabPane 
            tab={<span><SearchOutlined /> 文本搜索</span>} 
            key="text"
          >
            {renderTextSearch()}
          </TabPane>
          <TabPane 
            tab={<span><PictureOutlined /> 图片搜索</span>} 
            key="image"
          >
            {renderImageSearch()}
          </TabPane>
        </Tabs>
      </Card>

      <Divider />

      <div className="search-results-container">
        {renderSearchResults()}
      </div>
    </div>
  );
};

export default SearchPage;