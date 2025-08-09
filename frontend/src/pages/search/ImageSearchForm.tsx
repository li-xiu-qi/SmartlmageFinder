import React, { useState } from 'react';
import {
  Form,
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
  UploadOutlined
} from '@ant-design/icons';
import type { UploadFile, RcFile } from 'antd/es/upload';
import { TagInfo } from '@/types/models';
import { UnifiedImageSearchParams, VectorSearchTarget, SearchType } from '@/types/search';
import { IMAGE_SEARCH_TARGETS, UPLOAD_CONFIG } from './constants';
import { getImagePreviewUrl, getVectorSearchTargets } from './utils';
import ImageSearchUpload from './components/ImageSearchUpload';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface ImageSearchFormProps {
  onSearch: (params: UnifiedImageSearchParams) => void;
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
      const params: UnifiedImageSearchParams = {
        file: searchFile,
        search_type: SearchType.VECTOR
      } as any; // 兼容后端接受 form-data 与 search_type

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

  // 标签变更时自动应用（仅当已选择图片时才触发搜索）
  const handleTagsChange = async (values: string[]) => {
    form.setFieldsValue({ tags: values });
    if (searchFile) {
      await handleSearch();
    }
  };

  return (
    <Card className="search-form-card">      <Form
        form={form}
        layout="vertical"
        style={{ width: '100%' }}
      >
        <div className="upload-container">
          <ImageSearchUpload
            fileList={fileList}
            onFileChange={(file) => {
              setSearchFile(file);
              if (file) {
                getImagePreviewUrl(file).then(url => setImageUrl(url));
                setFileList([{ 
                  uid: '-1', 
                  name: file.name, 
                  status: 'done', 
                  url: URL.createObjectURL(file) 
                }]);
              } else {
                setFileList([]);
                setImageUrl('');
              }
            }}
            onImageUrlChange={setImageUrl}
            maxSize={UPLOAD_CONFIG.MAX_FILE_SIZE}
            imageUrl={imageUrl}
          />
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
            语义图像搜索
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
                onChange={handleTagsChange}
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
