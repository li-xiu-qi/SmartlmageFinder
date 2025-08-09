import React, { useEffect } from 'react';
import { Form, Input, Button, Select, DatePicker, Card, Row, Col, Divider, Space, Tooltip } from 'antd';
import { SearchOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import { TagInfo } from '@/types/models';
import { FuzzySearchParams } from '@/types/search';
import { parseTagsFromParam } from './utils';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface FuzzySearchFormProps {
  onSearch: (params: FuzzySearchParams) => void;
  loading: boolean;
  tags: TagInfo[];
}

/**
 * 模糊搜索表单 (LIKE)
 * 适合快速关键词粗匹配。相比语义检索速度更快但不具备语义理解。
 */
const FuzzySearchForm: React.FC<FuzzySearchFormProps> = ({ onSearch, loading, tags }) => {
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm();

  // 初始化表单
  useEffect(() => {
    const q = searchParams.get('q') || '';
    const tagsParam = searchParams.get('tags');
    const fieldsParam = searchParams.get('fields');

    const initial: any = { q };
    if (tagsParam) initial.tags = parseTagsFromParam(tagsParam);
    if (fieldsParam) initial.fields = fieldsParam.split(',');

    form.setFieldsValue(initial);
  }, [searchParams, form]);

  const submit = (values: any) => {
    const params: FuzzySearchParams = { q: values.q };
    if (values.fields && values.fields.length > 0) params.fields = values.fields;
    if (values.tags && values.tags.length > 0) params.tags = values.tags;
    if (values.date_range && values.date_range.length === 2) {
      params.start_date = new Date(values.date_range[0]).toISOString();
      params.end_date = new Date(values.date_range[1]).toISOString();
    }
    onSearch(params);
  };

  const handleTagsChange = (vals: string[]) => {
    form.setFieldsValue({ tags: vals });
    const values = form.getFieldsValue();
    if (values.q) submit(values);
  };

  return (
    <Card className="search-form-card">
      <Form form={form} layout="vertical" onFinish={submit}>
        <Row gutter={16}>
          <Col xs={24} md={18}>
            <Form.Item name="q" rules={[{ required: true, message: '请输入关键词' }]}>
              <Input
                placeholder="输入关键词 (LIKE 模糊匹配)"
                size="large"
                prefix={<SearchOutlined />}
                allowClear
              />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="fields"
          label={<span>匹配字段 <Tooltip title="选择进行 LIKE 匹配的列"><QuestionCircleOutlined style={{ marginLeft: 4 }} /></Tooltip></span>}
        >
          <Select mode="multiple" placeholder="默认: 标题 + 描述" allowClear>
            <Option value="title">标题</Option>
            <Option value="description">描述</Option>
            <Option value="filename">文件名</Option>
          </Select>
        </Form.Item>

        <Space>
          <Button type="primary" htmlType="submit" icon={<SearchOutlined />} loading={loading}>模糊搜索</Button>
        </Space>

        <Divider />
        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item name="tags" label="标签筛选">
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
            <Form.Item name="date_range" label="日期范围">
              <RangePicker
                className="date-range-picker"
                showTime={{ format: 'HH:mm' }}
                format="YYYY-MM-DD HH:mm"
              />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Card>
  );
};

export default FuzzySearchForm;
