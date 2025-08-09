import React from 'react';
import { Form, Row, Col, Select, DatePicker, Button, Space } from 'antd';
import { FilterOutlined, ReloadOutlined } from '@ant-design/icons';
import { TagInfo } from '@/types/models';
import { GetImagesListParams } from '@/types/image';
import { convertTagsToOptions } from '@/utils/typeConverters';

const { RangePicker } = DatePicker;
const { Option } = Select;

interface FilterFormProps {
  tags: TagInfo[];
  onFilter: (values: GetImagesListParams) => void;
  onReset: () => void;
  initialValues?: Partial<GetImagesListParams>;
  loading?: boolean;
}

/**
 * 图片筛选表单组件
 */
const FilterForm: React.FC<FilterFormProps> = ({
  tags,
  onFilter,
  onReset,
  initialValues,
  loading = false
}) => {
  const [form] = Form.useForm();

  // 处理表单提交
  const handleSubmit = (values: any) => {
    const filters: GetImagesListParams = {};

    // 设置排序字段和方向
    if (values.sort_by) {
      filters.sort_by = values.sort_by;
      filters.order = values.order || 'desc';
    }

    // 设置日期范围
    if (values.date_range && values.date_range.length === 2) {
      filters.start_date = values.date_range[0].format('YYYY-MM-DD');
      filters.end_date = values.date_range[1].format('YYYY-MM-DD');
    }

    // 设置标签
    if (values.tags && values.tags.length > 0) {
      filters.tags = values.tags;
    }

    onFilter(filters);
  };

  // 重置表单
  const handleReset = () => {
    form.resetFields();
    onReset();
  };

  return (
    <div className="filter-form-container">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          sort_by: 'created_at',
          order: 'desc',
          ...initialValues
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
                options={convertTagsToOptions(tags)}
              />
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
                <Button 
                  icon={<ReloadOutlined />} 
                  onClick={handleReset}
                  disabled={loading}
                >
                  重置
                </Button>
                <Button 
                  type="primary" 
                  icon={<FilterOutlined />} 
                  htmlType="submit"
                  loading={loading}
                >
                  筛选
                </Button>
              </Space>
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </div>
  );
};

export default FilterForm;
