import React, { useState, useEffect } from 'react';
import { Card, Spin, Typography, Empty, message } from 'antd';
import { TagsOutlined } from '@ant-design/icons';
import tagService from '@/services/tagService';
import { TagInfo } from '@/types/models';
import './styles.less';

// 导入拆分的组件
import TagCloud from './components/TagCloud';
import TagTable from './components/TagTable';
import TagSearch from './components/TagSearch';

const { Title, Text } = Typography;

const TagsPage: React.FC = () => {
  const [tags, setTags] = useState<TagInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchValue, setSearchValue] = useState('');

  // 获取热门标签
  useEffect(() => {
    fetchPopularTags();
  }, []);

  // 获取标签列表
  const fetchPopularTags = async () => {
    try {
      setLoading(true);
      const response = await tagService.getPopularTags({ limit: 100 });
      if (response.status === 'success' && response.data) {
        setTags(response.data);
      } else {
        message.error('获取热门标签失败');
      }
    } catch (error) {
      console.error('获取热门标签失败:', error);
      message.error('获取热门标签失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="tags-page">
      <Card>
        <Title level={4}>
          <TagsOutlined /> 标签管理
        </Title>
        <Text type="secondary">查看并管理所有图片标签，点击标签可查看相关图片</Text>

        <TagSearch value={searchValue} onChange={setSearchValue} />

        <Spin spinning={loading}>
          {tags.length > 0 ? (
            <>              {/* 标签云 */}
              <Card title="标签云" className="tag-cloud-card">
                <TagCloud tags={tags} searchValue={searchValue} />
              </Card>

              {/* 标签表格 */}
              <Card title="标签列表">
                <TagTable tags={tags} loading={loading} searchValue={searchValue} />
              </Card>
            </>
          ) : (
            <Card>
              <Empty                description={
                  <div className="empty-container">
                    <Title level={4}>暂无标签</Title>
                    <Text type="secondary">上传图片并为它们添加标签后，标签将显示在此处</Text>
                  </div>
                }
              />
            </Card>
          )}
        </Spin>
      </Card>
    </div>
  );
};

export default TagsPage;