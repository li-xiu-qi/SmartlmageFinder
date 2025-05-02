import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Tag,
  Button,
  Input,
  Space,
  Modal,
  Form,
  message,
  Spin,
  Typography,
  Row,
  Col
} from 'antd';
import { 
  EditOutlined, 
  DeleteOutlined, 
  PlusOutlined, 
  SearchOutlined, 
  TagsOutlined,
  PictureOutlined
} from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { tagService } from '@/services/api';
import { Tag as TagType } from '@/types';

const { Title, Text } = Typography;

// 解码可能的Unicode字符串
const decodeUnicode = (str: string): string => {
  try {
    // 尝试解码Unicode转义序列（如\u4f60\u597d）
    return str.replace(/\\u[\dA-F]{4}/gi, match => 
      String.fromCharCode(parseInt(match.replace(/\\u/g, ''), 16))
    );
  } catch (error) {
    console.error('Unicode解码失败:', error);
    return str; // 如果解码失败，返回原始字符串
  }
};

const TagsPage: React.FC = () => {
  const [tags, setTags] = useState<TagType[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  const navigate = useNavigate();

  // 获取所有标签
  useEffect(() => {
    fetchTags();
  }, []);

  // 获取标签列表
  const fetchTags = async () => {
    try {
      setLoading(true);
      const response = await tagService.getTags();
      if (response.status === 'success' && response.data) {
        setTags(response.data.tags || []);
      }
    } catch (error) {
      console.error('获取标签失败:', error);
      message.error('获取标签失败');
    } finally {
      setLoading(false);
    }
  };

  // 根据搜索条件过滤标签
  const filteredTags = tags.filter(tag => 
    tag.name.toLowerCase().includes(searchValue.toLowerCase())
  );

  // 表格列定义
  const columns = [
    {
      title: '标签',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Link to={`/images?tags=${text}`}>
          <Tag color="blue" style={{ fontSize: '14px', padding: '4px 8px' }}>
            {decodeUnicode(text)}
          </Tag>
        </Link>
      ),
    },
    {
      title: '使用次数',
      dataIndex: 'count',
      key: 'count',
      sorter: (a: TagType, b: TagType) => a.count - b.count,
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record: TagType) => (
        <Space size="middle">
          <Button 
            type="primary" 
            icon={<PictureOutlined />}
            size="small"
            onClick={() => navigate(`/images?tags=${record.name}`)}
          >
            查看图片
          </Button>
        </Space>
      ),
    },
  ];

  // 生成标签云样式
  const getTagColor = (count: number) => {
    const maxCount = Math.max(...tags.map(tag => tag.count));
    const colors = ['blue', 'cyan', 'geekblue', 'purple', 'magenta', 'red', 'volcano', 'orange', 'gold', 'lime', 'green'];
    const index = Math.min(Math.floor((count / maxCount) * colors.length), colors.length - 1);
    return colors[index];
  };

  // 计算标签字体大小
  const getTagFontSize = (count: number) => {
    const maxCount = Math.max(...tags.map(tag => tag.count));
    const minSize = 12;
    const maxSize = 24;
    const size = minSize + ((count / maxCount) * (maxSize - minSize));
    return Math.max(minSize, Math.min(maxSize, size));
  };

  return (
    <div className="tags-page">
      <Card>
        <Title level={4}>
          <TagsOutlined /> 标签管理
        </Title>
        <Text type="secondary">管理所有图片标签，点击标签可查看相关图片</Text>

        <div style={{ marginTop: 16, marginBottom: 16 }}>
          <Input
            placeholder="搜索标签..."
            prefix={<SearchOutlined />}
            onChange={(e) => setSearchValue(e.target.value)}
            style={{ width: 300 }}
          />
        </div>

        <Spin spinning={loading}>
          {tags.length > 0 ? (
            <>
              {/* 标签云 */}
              <Card title="标签云" style={{ marginBottom: 24 }}>
                <div style={{ padding: '16px 0' }}>
                  {filteredTags.map(tag => (
                    <Link to={`/images?tags=${tag.name}`} key={tag.name}>
                      <Tag 
                        color={getTagColor(tag.count)} 
                        style={{ 
                          fontSize: getTagFontSize(tag.count),
                          padding: '4px 8px',
                          margin: '0 8px 8px 0',
                          cursor: 'pointer'
                        }}
                      >
                        {decodeUnicode(tag.name)} ({tag.count})
                      </Tag>
                    </Link>
                  ))}
                </div>
              </Card>

              {/* 标签表格 */}
              <Card title="标签列表">
                <Table 
                  columns={columns} 
                  dataSource={filteredTags} 
                  rowKey="name"
                  pagination={{
                    pageSize: 10,
                    showSizeChanger: true,
                    pageSizeOptions: ['10', '20', '50', '100'],
                    showTotal: (total) => `共 ${total} 个标签`,
                  }}
                />
              </Card>
            </>
          ) : (
            <Card>
              <div style={{ textAlign: 'center', padding: '24px 0' }}>
                <Title level={4}>暂无标签</Title>
                <Text type="secondary">上传图片并为它们添加标签后，标签将显示在此处</Text>
              </div>
            </Card>
          )}
        </Spin>
      </Card>
    </div>
  );
};

export default TagsPage;