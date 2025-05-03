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
  message
} from 'antd';
import {
  SearchOutlined,
  UploadOutlined,
  PictureOutlined,
  FilterOutlined,
  ReloadOutlined,
  LoadingOutlined,
  InboxOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import { useSearchParams, useNavigate } from 'react-router-dom';
import type { UploadFile, UploadProps } from 'antd';
import type { RcFile } from 'antd/es/upload';
import { searchService, tagService } from '@/services/api';
import { Tag as TagType, ImageSearchResult } from '@/types';
import ImageCard from '@/components/ImageCard';
import { debounce } from 'lodash';

const { TabPane } = Tabs;
const { Option } = Select;
const { RangePicker } = DatePicker;
const { Dragger } = Upload;

// 定义搜索模式选项
const searchModes = [
  { value: 'vector', label: '向量搜索' },
  { value: 'text', label: '文本匹配' },
  { value: 'hybrid', label: '混合搜索' }
];

// 定义向量类型选项
const vectorTypes = [
  { value: 'title', label: '标题向量' },
  { value: 'description', label: '描述向量' },
  { value: 'mixed', label: '混合向量' },
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

  // 初始化表单值
  useEffect(() => {
    const query = searchParams.get('q');
    const mode = searchParams.get('mode') || 'vector';
    const vectorType = searchParams.get('vector_type') || 'mixed';
    const tagsParam = searchParams.get('tags');
    
    // 如果URL中有查询参数，设置表单值
    if (query) {
      form.setFieldsValue({ query });
      // 执行搜索
      handleTextSearch({ query, mode, vector_type: vectorType });
    }
    
    if (tagsParam) {
      const tagsArray = tagsParam.split(',').map(tag => tag.trim());
      form.setFieldsValue({ tags: tagsArray });
    }
    
    if (mode) {
      form.setFieldsValue({ mode });
    }
    
    if (vectorType) {
      form.setFieldsValue({ vector_type: vectorType });
    }
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

  // 执行文本搜索
  const handleTextSearch = async (values: any) => {
    try {
      const { query, mode, vector_type, field, tags, date_range } = values;
      
      if (!query || query.trim() === '') {
        message.warning('请输入搜索关键词');
        return;
      }
      
      setLoading(true);
      
      // 构建搜索参数
      const searchParams: any = {
        q: query,
        mode: mode || 'vector',
        vector_type: vector_type || 'mixed',
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
        mode: searchParams.mode,
        vector_type: searchParams.vector_type,
        ...(searchParams.tags ? { tags: searchParams.tags } : {})
      });
      
      // 调用搜索API
      const response = await searchService.searchByText(searchParams);
      
      if (response.status === 'success' && response.data) {
        setResults(response.data.results || []);
        setTotal(response.data.results.length);
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
      const params: any = {
        limit: 50,
      };
      
      // 添加标签过滤
      if (values.tags && values.tags.length > 0) {
        params.tags = values.tags.join(',');
      }
      
      // 添加日期范围过滤
      if (values.date_range && values.date_range.length === 2) {
        params.start_date = values.date_range[0].format('YYYY-MM-DD');
        params.end_date = values.date_range[1].format('YYYY-MM-DD');
      }
      
      // 调用图片搜索API
      const response = await searchService.searchByImage(searchImage, params);
      
      if (response.status === 'success' && response.data) {
        setResults(response.data.results || []);
        setTotal(response.data.results.length);
      }
    } catch (error) {
      console.error('图片搜索失败:', error);
      message.error('图片搜索失败，请稍后重试');
    } finally {
      setLoading(false);
    }
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
          mode: 'vector',
          vector_type: 'mixed',
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

        <div style={{ textAlign: 'right', marginBottom: 16 }}>
          <Button type="link" onClick={toggleAdvanced}>
            {showAdvanced ? '收起高级选项' : '显示高级选项'}
          </Button>
        </div>

        {showAdvanced && (
          <div className="advanced-options">
            <Row gutter={16}>
              <Col xs={24} md={8}>
                <Form.Item name="mode" label="搜索模式">
                  <Select>
                    {searchModes.map(mode => (
                      <Option key={mode.value} value={mode.value}>{mode.label}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col xs={24} md={8}>
                <Form.Item 
                  name="vector_type" 
                  label="向量类型"
                  tooltip="选择用于搜索的向量类型，仅在向量或混合搜索模式下有效"
                >
                  <Select>
                    {vectorTypes.map(type => (
                      <Option key={type.value} value={type.value}>{type.label}</Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col xs={24} md={8}>
                <Form.Item name="date_range" label="日期范围">
                  <RangePicker style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>

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
      <Form form={form}>
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

        <div style={{ textAlign: 'right', marginBottom: 16 }}>
          <Button type="link" onClick={toggleAdvanced}>
            {showAdvanced ? '收起高级选项' : '显示高级选项'}
          </Button>
        </div>

        {showAdvanced && (
          <div className="advanced-options">
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
        <div style={{ marginBottom: 16 }}>
          共找到 <strong>{total}</strong> 个结果
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