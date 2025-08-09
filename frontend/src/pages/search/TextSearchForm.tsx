import React, { useEffect } from 'react';
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
  QuestionCircleOutlined
} from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import { TagInfo } from '@/types/models';
import { UnifiedTextSearchParams, VectorSearchTarget } from '@/types/search';
import { VECTOR_SEARCH_TARGETS } from './constants';
import { parseTagsFromParam, getVectorSearchTargets } from './utils';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface TextSearchFormProps {
  onSearch: (params: UnifiedTextSearchParams) => void;
  loading: boolean;
  tags: TagInfo[];
}

/**
 * 文本搜索表单组件
 */
const TextSearchForm: React.FC<TextSearchFormProps> = ({ onSearch, loading, tags }) => {
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm();
  const isVectorSearch = true; // 仅向量搜索
  
  // 标签变更时自动应用过滤（仅当已填写关键词时）
  const handleTagsChange = (values: string[]) => {
    form.setFieldsValue({ tags: values });
    const current = form.getFieldsValue();
    // 只有在存在关键词时才触发搜索（后端 q 为必填）
    if (current.q && String(current.q).trim().length > 0) {
      // 直接复用提交逻辑
      handleSubmit({ ...current, tags: values });
    }
  };
    // 初始化表单值
  useEffect(() => {
  const query = searchParams.get('q');
    const tagsParam = searchParams.get('tags');
    const vectorTargets = searchParams.get('vector_targets')?.split(',');
    
    // 设置默认表单值
  const initialValues: Record<string, string | string[]> = { q: query || '' };

    // 如果有标签参数，解析并设置
    if (tagsParam) {
      initialValues.tags = parseTagsFromParam(tagsParam);
    }
    
    // 如果有向量搜索目标参数，设置
    if (vectorTargets && vectorTargets.length > 0) {
      initialValues.vector_targets = vectorTargets;
    } else {
      initialValues.vector_targets = [VectorSearchTarget.TITLE, VectorSearchTarget.DESCRIPTION, VectorSearchTarget.IMAGE];
    }

    // 设置表单初始值
    form.setFieldsValue(initialValues);
  }, [searchParams, form]);
    // 执行文本搜索
  const handleSubmit = (values: Record<string, any>) => {
    // 构造搜索参数
  const params: UnifiedTextSearchParams = { q: values.q };
  params.vector_targets = getVectorSearchTargets(values.vector_targets);

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

  return (
    <Card className="search-form-card">
      <Form
        form={form}
        onFinish={handleSubmit}
        layout="vertical"
        initialValues={{
          vector_targets: [VectorSearchTarget.TITLE, VectorSearchTarget.DESCRIPTION, VectorSearchTarget.IMAGE]
        }}
      >
        <Row gutter={16}>
          <Col xs={24} md={18}>
            <Form.Item 
              name="q" 
              rules={[{ required: true, message: '请输入搜索关键词！' }]}
            >
              <Input
                placeholder="输入关键词 (多向量语义检索)"
                size="large"
                prefix={<SearchOutlined />}
                allowClear
              />
            </Form.Item>
          </Col>
        </Row>

  {isVectorSearch && (
          <Form.Item
            name="vector_targets"
            label={
              <span>
                向量搜索目标 
                <Tooltip 
                  title="选择用于向量搜索的字段"
                  getPopupContainer={(trigger) => trigger.parentElement || document.body}
                >
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
        )}        <Space>
          <Button 
            type="primary" 
            htmlType="submit" 
            icon={<SearchOutlined />} 
            loading={loading}
          >
            搜索
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

export default TextSearchForm;
