import React, { useState } from 'react';
import {
  Form,
  Upload,
  Button,
  Select,
  DatePicker,
  Space,
  Divider,
  Card,
  Row,
  Col,
  message,
  Input
} from 'antd';
import {
  UploadOutlined,
  InboxOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import type { UploadFile, RcFile } from 'antd/es/upload';
import { TagInfo } from '@/types/models';
import { ImageSearchParams, VectorSearchTarget } from '@/types/search';
import { IMAGE_SEARCH_TARGETS, UPLOAD_CONFIG } from './constants';
import { validateImageFile, getImagePreviewUrl, getVectorSearchTargets } from './utils';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Dragger } = Upload;

interface ImageSearchFormProps {
  onSearch: (params: ImageSearchParams) => void;
  loading: boolean;
  tags: TagInfo[];
}

/**
 * 图像搜索表单组件
 */
const ImageSearchForm: React.FC<ImageSearchFormProps> = ({ onSearch, loading, tags }) => {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [searchFile, setSearchFile] = useState<RcFile | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');
  const [selectedSearchTargets, setSelectedSearchTargets] = useState<string[]>([VectorSearchTarget.IMAGE]);

  // 处理上传前的验证
  const beforeUpload = (file: RcFile) => {
    const validation = validateImageFile(file, UPLOAD_CONFIG.MAX_FILE_SIZE);
    
    if (!validation.valid) {
      message.error(validation.message);
      return false;
    }
    
    // 更新搜索文件和预览
    setSearchFile(file);
    getImagePreviewUrl(file).then(url => setImageUrl(url));
    
    // 更新文件列表
    setFileList([{ uid: '-1', name: file.name, status: 'done', url: URL.createObjectURL(file) }]);
    
    // 阻止默认上传行为
    return false;
  };

  // 处理文件移除
  const handleRemove = () => {
    setFileList([]);
    setSearchFile(null);
    setImageUrl('');
    return true;
  };

  // 处理搜索目标变化
  const handleSearchTargetsChange = (targets: string[]) => {
    // 确保至少选择一个目标
    if (targets.length === 0) {
      message.warning('请至少选择一个搜索目标');
      return;
    }
    
    setSelectedSearchTargets(targets);
  };
    // 执行图片搜索
  const handleSearch = async () => {
    if (!searchFile) {
      message.error('请先上传一张图片');
      return;
    }

    try {
      // 获取表单值
      const values = await form.validateFields();
      
      // 构造搜索参数
      const params: ImageSearchParams = {
        file: searchFile
      };

      // 设置搜索目标
      if (selectedSearchTargets.length > 0) {
        params.search_targets = getVectorSearchTargets(selectedSearchTargets);
      }

      // 添加高级搜索参数（如果有）
      if (values.tags && values.tags.length > 0) {
        params.tags = values.tags;
      }

      if (values.filename) {
        params.filename = values.filename;
      }

      if (values.date_range && values.date_range.length === 2) {
        const startDate = new Date(values.date_range[0]);
        const endDate = new Date(values.date_range[1]);
        params.start_date = startDate.toISOString();
        params.end_date = endDate.toISOString();
      }

      // 调用搜索
      onSearch(params);
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  // 上传组件配置
  const uploadProps = {
    name: 'file',
    multiple: false,
    fileList,
    beforeUpload,
    onRemove: handleRemove,
    accept: UPLOAD_CONFIG.ACCEPTED_TYPES.join(',')
  };

  return (
    <Card className="search-form-card">      <Form
        form={form}
        layout="vertical"
        initialValues={{
          search_type: 'vector'
        }}
        style={{ width: '100%' }}
      >
        <div className="upload-container">
          {fileList.length === 0 ? (
            <Dragger {...uploadProps}>
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽图片到此区域进行上传</p>
              <p className="ant-upload-hint">
                支持单张图片上传，文件大小不超过{UPLOAD_CONFIG.MAX_FILE_SIZE}MB
              </p>
            </Dragger>
          ) : (
            <div className="image-preview">
              {imageUrl && (
                <div className="preview-container">
                  <img src={imageUrl} alt="搜索图片" />
                  <Button 
                    icon={<DeleteOutlined />} 
                    onClick={handleRemove} 
                    className="remove-btn"
                    danger
                  >
                    移除
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>

        <Form.Item label="搜索目标">
          <Select
            mode="multiple"
            value={selectedSearchTargets}
            onChange={handleSearchTargetsChange}
            className="search-targets-select"
          >
            {IMAGE_SEARCH_TARGETS.map(target => (
              <Option key={target.value} value={target.value}>{target.label}</Option>
            ))}
          </Select>
        </Form.Item>

        <Space>
          <Button
            type="primary"
            onClick={handleSearch}
            icon={<UploadOutlined />}
            loading={loading}
            disabled={fileList.length === 0}
          >
            以图搜图
          </Button>
        </Space>

        <Divider />
        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              name="tags"
              label="标签筛选"
            >
              <Select
                mode="multiple"
                placeholder="选择标签筛选"
                optionFilterProp="children"
                allowClear
              >
                {tags.map(tag => (
                  <Option key={tag.tag} value={tag.tag}>{tag.tag} ({tag.count})</Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item
              name="date_range"
              label="日期范围"
            >
              <RangePicker
                className="date-range-picker"
                showTime={{ format: 'HH:mm' }}
                format="YYYY-MM-DD HH:mm"
              />
            </Form.Item>
          </Col>
        </Row>
        <Form.Item
          name="filename"
          label="文件名包含"
        >
          <Input placeholder="输入文件名关键词" />
        </Form.Item>
      </Form>
    </Card>
  );
};

export default ImageSearchForm;
