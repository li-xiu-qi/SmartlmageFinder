import React, { useState, useEffect } from 'react';
import {
  Form,
  Input,
  Button,
  Select,
  DatePicker,
  Space,
  Divider,
  Card,
  Row,
  Col,
  Tooltip
} from 'antd';
import {
  SearchOutlined,
  FilterOutlined,
  QuestionCircleOutlined
} from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import { TagInfo } from '@/types/models';
import { TextSearchParams, VectorSearchTarget } from '@/types/search';
import { TEXT_SEARCH_TYPES, ADVANCED_SEARCH_TYPES, VECTOR_SEARCH_TARGETS } from './constants';
import { mapToApiSearchType, parseTagsFromParam, getVectorSearchTargets } from './utils';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface TextSearchFormProps {
  onSearch: (params: TextSearchParams) => void;
  loading: boolean;
  tags: TagInfo[];
}

/**
 * 文本搜索表单组件
 */
const TextSearchForm: React.FC<TextSearchFormProps> = ({ onSearch, loading, tags }) => {
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm();
  const [showAdvanced, setShowAdvanced] = useState(false);

  // 从Form.useWatch获取当前搜索类型值
  const searchType = Form.useWatch('search_type', form);
  const isVectorSearch = searchType === 'vector' || searchType === 'multi';
  
  // 初始化表单值
  useEffect(() => {
    const query = searchParams.get('q');
    const searchType = searchParams.get('search_type') || 'both';
    const tagsParam = searchParams.get('tags');
    const startDate = searchParams.get('start_date');
    const endDate = searchParams.get('end_date');
    const filename = searchParams.get('filename');
    const vectorTargets = searchParams.get('vector_targets')?.split(',');
    
    // 设置默认表单值
    const initialValues: Record<string, string | string[]> = {
      search_type: searchType,
      q: query || ''
    };

    // 如果有标签参数，解析并设置
    if (tagsParam) {
      initialValues.tags = parseTagsFromParam(tagsParam);
    }
    
    // 如果有向量搜索目标参数，设置
    if (vectorTargets && vectorTargets.length > 0) {
      initialValues.vector_targets = vectorTargets;
    }

    // 设置表单初始值
    form.setFieldsValue(initialValues);

    // 如果有高级参数，显示高级搜索选项
    if (startDate || endDate || filename || isVectorSearch) {
      setShowAdvanced(true);
    }
  }, [searchParams, form, isVectorSearch]);
  
  // 执行文本搜索
  const handleSubmit = (values: Record<string, any>) => {
    // 构造搜索参数
    const params: TextSearchParams = {
      q: values.q
    };

    // 添加搜索类型
    params.search_type = mapToApiSearchType(values.search_type);
    
    // 设置向量搜索目标
    if (values.search_type === 'vector' || values.search_type === 'multi') {
      params.vector_targets = getVectorSearchTargets(values.vector_targets);
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
  };

  // 切换高级搜索选项显示
  const toggleAdvanced = () => {
    setShowAdvanced(!showAdvanced);
  };

  return (
    <Card className="search-form-card">
      <Form
        form={form}
        onFinish={handleSubmit}
        layout="vertical"
        initialValues={{
          search_type: 'both',
          vector_targets: [VectorSearchTarget.TITLE, VectorSearchTarget.DESCRIPTION]
        }}
      >
        <Row gutter={16}>
          <Col xs={24} md={18}>
            <Form.Item 
              name="q" 
              rules={[{ required: true, message: '请输入搜索关键词！' }]}
            >
              <Input
                placeholder="输入关键词搜索图片..."
                size="large"
                prefix={<SearchOutlined />}
                allowClear
              />
            </Form.Item>
          </Col>
          <Col xs={24} md={6}>
            <Form.Item name="search_type">
              <Select size="large">
                {TEXT_SEARCH_TYPES.map(type => (
                  <Option key={type.value} value={type.value}>{type.label}</Option>
                ))}
                {ADVANCED_SEARCH_TYPES.map(type => (
                  <Option key={type.value} value={type.value}>{type.label}</Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        {isVectorSearch && (
          <Form.Item
            name="vector_targets"
            label={
              <span>
                向量搜索目标 
                <Tooltip title="选择用于向量搜索的字段">
                  <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                </Tooltip>
              </span>
            }
          >
            <Select 
              mode="multiple" 
              placeholder="选择搜索目标"
              className="search-targets-select"
            >
              {VECTOR_SEARCH_TARGETS.map(target => (
                <Option key={target.value} value={target.value}>{target.label}</Option>
              ))}
            </Select>
          </Form.Item>
        )}

        <Space>
          <Button 
            type="primary" 
            htmlType="submit" 
            icon={<SearchOutlined />} 
            loading={loading}
          >
            搜索
          </Button>
          <Button 
            type="link" 
            icon={<FilterOutlined />} 
            onClick={toggleAdvanced}
          >
            {showAdvanced ? '隐藏' : '显示'}高级选项
          </Button>
        </Space>

        {showAdvanced && (
          <>
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
          </>
        )}
      </Form>
    </Card>
  );
};

export default TextSearchForm;
