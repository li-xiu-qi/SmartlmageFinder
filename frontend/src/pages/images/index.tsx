import React, { useState, useEffect } from 'react';
import { 
  Row, 
  Col, 
  Card, 
  Form, 
  Select, 
  DatePicker, 
  Space, 
  Button, 
  Pagination, 
  Empty, 
  Spin, 
  message,
  Drawer,
  Radio,
  Tag,
  Popconfirm
} from 'antd';
import { 
  FilterOutlined, 
  SortAscendingOutlined, 
  AppstoreOutlined, 
  BarsOutlined,
  DeleteOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useNavigate, useSearchParams } from 'react-router-dom';
import ImageCard from '@/components/ImageCard';
import { imageService, tagService } from '@/services/api';
import { Image, ImageDetail, Tag as TagType, ImageListParams } from '@/types';
import ImageDetailView from './detail';
import { getImageUrl } from '@/utils/format';

const { Option } = Select;
const { RangePicker } = DatePicker;

const ImagesPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // 状态定义
  const [loading, setLoading] = useState(false);
  const [images, setImages] = useState<Image[]>([]);
  const [tags, setTags] = useState<TagType[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [selectedImage, setSelectedImage] = useState<ImageDetail | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  // 筛选条件
  const [form] = Form.useForm();
  const [filterValues, setFilterValues] = useState<ImageListParams>({});

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

  // 处理URL中的查询参数
  useEffect(() => {
    const tagsParam = searchParams.get('tags');
    if (tagsParam) {
      const tagsArray = tagsParam.split(',').map(tag => tag.trim());
      form.setFieldsValue({ tags: tagsArray });
      setFilterValues(prev => ({ ...prev, tags: tagsArray }));
    }
  }, [searchParams, form]);

  // 获取图片数据
  useEffect(() => {
    const fetchImages = async () => {
      try {
        setLoading(true);
        const params: ImageListParams = {
          ...filterValues,
          page,
          page_size: pageSize,
        };

        const response = await imageService.getImages(params);
        if (response.status === 'success' && response.data) {
          setImages(response.data.images || []);
          setTotal(response.metadata?.total || 0);
        }
      } catch (error) {
        console.error('获取图片失败:', error);
        message.error('获取图片数据失败');
      } finally {
        setLoading(false);
      }
    };

    fetchImages();
  }, [page, pageSize, filterValues]);

  // 处理筛选表单提交
  const handleFilterSubmit = async (values: any) => {
    const filters: ImageListParams = {};

    if (values.sort_by) {
      filters.sort_by = values.sort_by;
      filters.order = values.order || 'desc';
    }

    if (values.date_range && values.date_range.length === 2) {
      filters.start_date = values.date_range[0].format('YYYY-MM-DD');
      filters.end_date = values.date_range[1].format('YYYY-MM-DD');
    }

    if (values.tags && values.tags.length > 0) {
      filters.tags = values.tags;
    }

    setFilterValues(filters);
    setPage(1); // 重置为第一页
  };

  // 重置筛选条件
  const resetFilters = () => {
    form.resetFields();
    setFilterValues({});
    setPage(1);
  };

  // 处理图片点击事件，打开详情抽屉
  const handleImageClick = async (image: Image) => {
    try {
      setLoading(true);
      const response = await imageService.getImageDetail(image.uuid);
      if (response.status === 'success' && response.data) {
        setSelectedImage(response.data);
        setDetailVisible(true);
      }
    } catch (error) {
      console.error('获取图片详情失败:', error);
      message.error('获取图片详情失败');
    } finally {
      setLoading(false);
    }
  };

  // 关闭详情抽屉
  const handleDetailClose = () => {
    setDetailVisible(false);
    setSelectedImage(null);
  };

  // 删除图片
  const handleDeleteImage = async (uuid: string) => {
    try {
      setLoading(true);
      const response = await imageService.deleteImage(uuid);
      if (response.status === 'success') {
        message.success('图片删除成功');
        // 重新获取当前页的数据
        const updatedImages = images.filter(img => img.uuid !== uuid);
        if (updatedImages.length === 0 && page > 1) {
          setPage(page - 1);
        } else {
          setImages(updatedImages);
          setTotal(prev => prev - 1);
        }
        // 关闭详情抽屉
        setDetailVisible(false);
      }
    } catch (error) {
      console.error('删除图片失败:', error);
      message.error('删除图片失败');
    } finally {
      setLoading(false);
    }
  };

  // 图片详情更新后的处理
  const handleImageUpdate = (updatedImage: ImageDetail) => {
    // 更新列表中的图片数据
    setImages(prevImages => 
      prevImages.map(img => 
        img.uuid === updatedImage.uuid 
          ? { ...img, ...updatedImage } 
          : img
      )
    );
  };

  // 渲染筛选表单
  const renderFilterForm = () => (
    <Card style={{ marginBottom: 16 }}>
      <Form
        form={form}
        layout="vertical"
        onFinish={handleFilterSubmit}
        initialValues={{
          sort_by: 'created_at',
          order: 'desc',
        }}
      >
        <Row gutter={16}>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="时间范围" name="date_range">
              <RangePicker style={{ width: '100%' }} />
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="标签" name="tags">
              <Select
                mode="multiple"
                placeholder="选择标签"
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
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="排序字段" name="sort_by">
              <Select style={{ width: '100%' }}>
                <Option value="created_at">上传时间</Option>
                <Option value="title">标题</Option>
                <Option value="file_size">文件大小</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24} sm={12} md={8} lg={6}>
            <Form.Item label="排序方向" name="order">
              <Select style={{ width: '100%' }}>
                <Option value="desc">降序</Option>
                <Option value="asc">升序</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24}>
            <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
              <Space>
                <Button icon={<ReloadOutlined />} onClick={resetFilters}>
                  重置
                </Button>
                <Button type="primary" icon={<FilterOutlined />} htmlType="submit">
                  筛选
                </Button>
              </Space>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Card>
  );

  // 渲染视图控制栏
  const renderViewControls = () => (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, alignItems: 'center' }}>
      <div>
        <span>共 {total} 张图片</span>
      </div>
      <Space>
        <Radio.Group value={viewMode} onChange={e => setViewMode(e.target.value)}>
          <Radio.Button value="grid"><AppstoreOutlined /> 网格</Radio.Button>
          <Radio.Button value="list"><BarsOutlined /> 列表</Radio.Button>
        </Radio.Group>
      </Space>
    </div>
  );

  // 渲染图片列表
  const renderImageGrid = () => {
    if (images.length === 0) {
      return <Empty description="暂无图片" />;
    }

    if (viewMode === 'grid') {
      return (
        <Row gutter={[16, 16]}>
          {images.map(image => (
            <Col xs={12} sm={8} md={6} lg={4} key={image.uuid}>
              <ImageCard 
                image={image} 
                onClick={handleImageClick} 
                showTags={true} 
              />
            </Col>
          ))}
        </Row>
      );
    } else {
      return (
        <div>
          {images.map(image => (
            <Card 
              style={{ marginBottom: 16 }}
              key={image.uuid}
            >
              <div style={{ display: 'flex' }}>
                <div style={{ width: 100, height: 100, overflow: 'hidden', marginRight: 16 }}>
                  <img 
                    src={getImageUrl(image.filepath)} 
                    alt={image.title}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <h3 style={{ margin: '0 0 8px' }}>{image.title}</h3>
                  <p style={{ color: 'rgba(0, 0, 0, 0.45)', margin: '0 0 8px' }}>
                    上传时间: {new Date(image.created_at).toLocaleString()}
                  </p>
                  <div>
                    {image.tags.map(tag => (
                      <Tag key={tag}>{tag}</Tag>
                    ))}
                  </div>
                </div>
                <div>
                  <Button type="link" onClick={() => handleImageClick(image)}>查看详情</Button>
                  <Popconfirm
                    title="确定要删除这张图片吗？"
                    onConfirm={() => handleDeleteImage(image.uuid)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button type="link" danger icon={<DeleteOutlined />}>删除</Button>
                  </Popconfirm>
                </div>
              </div>
            </Card>
          ))}
        </div>
      );
    }
  };

  return (
    <div className="images-page">
      <Spin spinning={loading}>
        {renderFilterForm()}
        {renderViewControls()}
        {renderImageGrid()}
        
        {total > 0 && (
          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Pagination
              current={page}
              pageSize={pageSize}
              total={total}
              onChange={(p, ps) => {
                setPage(p);
                setPageSize(ps);
              }}
              showSizeChanger
              showQuickJumper
              showTotal={total => `共 ${total} 张图片`}
            />
          </div>
        )}

        {/* 图片详情抽屉 */}
        {selectedImage && (
          <Drawer
            title="图片详情"
            placement="right"
            closable={true}
            onClose={handleDetailClose}
            open={detailVisible}
            width={640}
            destroyOnClose
          >
            <ImageDetailView 
              image={selectedImage} 
              onUpdate={handleImageUpdate} 
              onDelete={handleDeleteImage} 
            />
          </Drawer>
        )}
      </Spin>
    </div>
  );
};

export default ImagesPage;