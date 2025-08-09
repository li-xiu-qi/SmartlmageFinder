import React from 'react';
import { Table, Tag as AntTag, Button, Space } from 'antd';
import { PictureOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { TagInfo } from '@/types/models';
import '../styles.less';

interface TagTableProps {
  tags: TagInfo[];
  loading: boolean;
  searchValue?: string;
}

const TagTable: React.FC<TagTableProps> = ({ tags, loading, searchValue = '' }) => {
  const navigate = useNavigate();

  // 根据搜索条件过滤标签
  const filteredTags = tags.filter(tag =>
    tag.tag.toLowerCase().includes(searchValue.toLowerCase())
  );

  // 表格列定义
  const columns = [
    {
      title: '标签',
      dataIndex: 'tag',
      key: 'tag',      render: (text: string) => (
        <Link to={`/images?tags=${text}`}>
          <AntTag color="blue" className="tag-label">
            {text}
          </AntTag>
        </Link>
      ),
    },
    {
      title: '使用次数',
      dataIndex: 'count',
      key: 'count',
      sorter: (a: TagInfo, b: TagInfo) => a.count - b.count,
    },
    {      title: '操作',
      key: 'action',
      render: (_: unknown, record: TagInfo) => (
        <Space size="middle">
          <Button
            type="primary"
            icon={<PictureOutlined />}
            size="small"
            onClick={() => navigate(`/images?tags=${record.tag}`)}
          >
            查看图片
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={filteredTags}
      rowKey="tag"
      loading={loading}
      pagination={{
        pageSize: 10,
        showSizeChanger: true,
        pageSizeOptions: ['10', '20', '50', '100'],
        showTotal: (total) => `共 ${total} 个标签`,
      }}
    />
  );
};

export default TagTable;
