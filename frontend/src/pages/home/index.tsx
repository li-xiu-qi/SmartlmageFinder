import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, List, Tag, Spin, Empty } from 'antd';
import { Link } from 'react-router-dom';
import { PictureOutlined, CheckCircleOutlined, WarningOutlined, TagsOutlined } from '@ant-design/icons';
import { imageService, systemService, tagService } from '@/services/api';
import { Tag as TagType, Image, SystemStatus } from '@/types';
import { getImageUrl } from '@/utils/format';

const HomePage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [recentImages, setRecentImages] = useState<Image[]>([]);
  const [tags, setTags] = useState<TagType[]>([]);
  const [systemStats, setSystemStats] = useState<{
    totalImages: number;
    status: string;
    totalTags: number;
  }>({
    totalImages: 0,
    status: 'unknown',
    totalTags: 0,
  });

  // 获取首页所需数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // 并行请求数据
        const [imagesResponse, tagsResponse, systemResponse] = await Promise.all([
          imageService.getImages({ page: 1, page_size: 8, sort_by: 'created_at', order: 'desc' }),
          tagService.getTags(),
          systemService.getSystemStatus(),
        ]);

        // 处理图片数据
        if (imagesResponse.status === 'success' && imagesResponse.data) {
          setRecentImages(imagesResponse.data.images || []);
        }

        // 处理标签数据
        if (tagsResponse.status === 'success' && tagsResponse.data) {
          // 排序标签并只取前20个
          const sortedTags = [...tagsResponse.data.tags]
            .sort((a, b) => b.count - a.count)
            .slice(0, 20);
          setTags(sortedTags);
          
          // 设置标签总数
          const totalTags = tagsResponse.data.tags?.length || 0;
          setSystemStats(prev => ({ ...prev, totalTags }));
        }

        // 处理系统状态数据
        if (systemResponse.status === 'success' && systemResponse.data) {
          const sysData = systemResponse.data as SystemStatus;
          setSystemStats(prev => ({
            ...prev,
            totalImages: sysData.storage.total_images,
            status: sysData.system.status
          }));
        }
      } catch (error) {
        console.error('获取首页数据失败:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // 获取随机颜色，基于标签使用频率
  const getTagColor = (count: number) => {
    const maxCount = tags.length > 0 ? Math.max(...tags.map(tag => tag.count)) : 0;
    const minCount = tags.length > 0 ? Math.min(...tags.map(tag => tag.count)) : 0;
    
    const colors = ['blue', 'cyan', 'geekblue', 'gold', 'green', 'lime', 'magenta', 'orange', 'purple', 'red', 'volcano'];
    
    if (maxCount === minCount) return colors[Math.floor(Math.random() * colors.length)];
    
    const index = Math.floor(((count - minCount) / (maxCount - minCount)) * (colors.length - 1));
    return colors[index];
  };

  return (
    <div className="home-page">
      <Spin spinning={loading}>
        {/* 状态卡片 */}
        <Row gutter={16} className="gutter-row">
          <Col xs={24} sm={8}>
            <Card className="stat-card">
              <Statistic
                title="系统状态"
                value={systemStats.status === 'healthy' ? '正常' : '异常'}
                valueStyle={{ color: systemStats.status === 'healthy' ? '#3f8600' : '#cf1322' }}
                prefix={systemStats.status === 'healthy' ? <CheckCircleOutlined /> : <WarningOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card className="stat-card">
              <Statistic
                title="图片总数"
                value={systemStats.totalImages}
                prefix={<PictureOutlined />}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card className="stat-card">
              <Statistic
                title="标签总数"
                value={systemStats.totalTags}
                prefix={<TagsOutlined />}
              />
            </Card>
          </Col>
        </Row>

        {/* 最近上传图片 */}
        <div className="recent-images">
          <h2 className="section-title">最近上传图片</h2>
          {recentImages.length > 0 ? (
            <Row gutter={[16, 16]}>
              {recentImages.map(image => (
                <Col xs={12} sm={8} md={6} key={image.uuid}>
                  <Link to={`/images/${image.uuid}`}>
                    <Card
                      hoverable
                      cover={
                        <div className="image-cover">
                          <img alt={image.title} src={getImageUrl(image.filepath)} />
                        </div>
                      }
                      className="image-card"
                    >
                      <Card.Meta
                        title={image.title}
                        description={
                          <span className="image-meta">
                            {new Date(image.created_at).toLocaleDateString()}
                          </span>
                        }
                      />
                    </Card>
                  </Link>
                </Col>
              ))}
            </Row>
          ) : (
            <Empty description="暂无图片" />
          )}
        </div>

        {/* 热门标签 */}
        <div className="hot-tags" style={{ marginTop: 24 }}>
          <h2 className="section-title">热门标签</h2>
          {tags.length > 0 ? (
            <div>
              {tags.map(tag => (
                <Link to={`/images?tags=${tag.name}`} key={tag.name}>
                  <Tag 
                    color={getTagColor(tag.count)} 
                    className="tag-item"
                  >
                    {tag.name} ({tag.count})
                  </Tag>
                </Link>
              ))}
            </div>
          ) : (
            <Empty description="暂无标签" />
          )}
        </div>
      </Spin>
    </div>
  );
};

export default HomePage;