import React, { useState } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Spin,
  Empty,
  Tag,
  Row,
  Col,
  message,
  Select
} from 'antd';
import {
  SearchOutlined,
  RobotOutlined,
  TagOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface AIRecommendation {
  image: {
    id: number;
    filename: string;
    filepath: string;
    title?: string;
    description?: string;
    tags?: string[];
    score?: number;
    file_size?: number;
    file_type?: string;
    width?: number;
    height?: number;
    created_at?: string;
  };
  ai_reason: string;
  relevance_score: number;
}

interface AIResponse {
  query: string;
  recommendations: AIRecommendation[];
  search_summary: {
    total_found: number;
    displayed: number;
    used_ai: boolean;
  };
  ai_analysis: string;
  timestamp: string;
}

const API_BASE_URL = 'http://localhost:10051';

const AIPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('text');
  const [vectorType, setVectorType] = useState('image');
  const [tags, setTags] = useState('');
  const [limit, setLimit] = useState(8);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<AIResponse | null>(null);
  const [useAI, setUseAI] = useState(true);
  const navigate = useNavigate();

  const handleSearch = async () => {
    if (!query.trim()) {
      message.warning('请输入搜索关键词');
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams({
        query,
        search_type: searchType,
        vector_type: vectorType,
        limit: limit.toString(),
        include_ai_reasoning: useAI.toString()
      });

      if (tags.trim()) {
        params.append('tags', tags.trim());
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/ai/recommend?${params}`);
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error?.message || '搜索失败');
      }
      
      setResults(data);
    } catch (error) {
      message.error(error instanceof Error ? error.message : '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  const handleImageClick = (imageId: number) => {
    navigate(`/images/${imageId}`);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getImageUrl = (filename: string) => {
    return `http://localhost:10050/static/images/${filename}`;
  };

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <Title level={2}>
        <RobotOutlined /> AI智能图片推荐
      </Title>
      
      <Card style={{ marginBottom: 24 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Input
            placeholder="请输入您想搜索的内容，例如：美丽的日落、科技感建筑..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onPressEnter={handleSearch}
            size="large"
            prefix={<SearchOutlined />}
          />
          
          <Row gutter={16}>
            <Col span={6}>
              <Select
                value={searchType}
                onChange={setSearchType}
                style={{ width: '100%' }}
                placeholder="搜索类型"
              >
                <Option value="text">文本搜索</Option>
                <Option value="vector">向量搜索</Option>
                <Option value="similar">相似搜索</Option>
                <Option value="filtered">过滤搜索</Option>
              </Select>
            </Col>
            <Col span={6}>
              <Select
                value={vectorType}
                onChange={setVectorType}
                style={{ width: '100%' }}
                placeholder="向量类型"
              >
                <Option value="image">图片内容</Option>
                <Option value="title">标题</Option>
                <Option value="description">描述</Option>
              </Select>
            </Col>
            <Col span={6}>
              <Input
                placeholder="标签过滤（用逗号分隔）"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                prefix={<TagOutlined />}
              />
            </Col>
            <Col span={6}>
              <Input
                type="number"
                placeholder="结果数量"
                value={limit}
                onChange={(e) => setLimit(parseInt(e.target.value) || 8)}
                min={1}
                max={20}
              />
            </Col>
          </Row>
          
          <Row gutter={16}>
            <Col span={12}>
              <Button
                type="primary"
                size="large"
                onClick={handleSearch}
                loading={loading}
                icon={<SearchOutlined />}
                style={{ width: '100%' }}
              >
                AI智能搜索
              </Button>
            </Col>
            <Col span={12}>
              <Button
                onClick={() => setUseAI(!useAI)}
                icon={<RobotOutlined />}
                style={{ width: '100%' }}
              >
                {useAI ? '启用AI分析' : '仅显示搜索结果'}
              </Button>
            </Col>
          </Row>
        </Space>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" tip="AI正在分析图片..." />
        </div>
      )}

      {!loading && results && (
        <>
          {results.ai_analysis && (
            <Card style={{ marginBottom: 16 }}>
              <Text strong>AI分析：</Text>
              <Paragraph>{results.ai_analysis}</Paragraph>
              <Text type="secondary">
                共找到 {results.search_summary.total_found} 张图片，
                显示 {results.search_summary.displayed} 张
                {results.search_summary.used_ai && '（AI优化推荐）'}
              </Text>
            </Card>
          )}

          {results.recommendations.length === 0 ? (
            <Empty description="未找到相关图片" />
          ) : (
            <Row gutter={[16, 16]}>
              {results.recommendations.map((rec) => (
                <Col key={rec.image.id} xs={24} sm={12} md={8} lg={6}>
                  <Card
                    hoverable
                    cover={
                      <img
                        alt={rec.image.title || rec.image.filename}
                        src={getImageUrl(rec.image.filename)}
                        style={{
                          height: 200,
                          objectFit: 'cover',
                          borderRadius: '8px 8px 0 0'
                        }}
                        onClick={() => handleImageClick(rec.image.id)}
                      />
                    }
                    actions={[
                      <Button
                        type="link"
                        size="small"
                        onClick={() => handleImageClick(rec.image.id)}
                      >
                        查看详情
                      </Button>
                    ]}
                  >
                    <Card.Meta
                      title={rec.image.title || rec.image.filename}
                      description={
                        <div>
                          <Text type="secondary" style={{ fontSize: 12 }}>
                            {rec.ai_reason}
                          </Text>
                          <div style={{ marginTop: 8 }}>
                            <Tag color="blue">
                              相关度: {(rec.relevance_score * 100).toFixed(0)}%
                            </Tag>
                          </div>
                          {rec.image.tags && rec.image.tags.length > 0 && (
                            <div style={{ marginTop: 8 }}>
                              {rec.image.tags.slice(0, 3).map(tag => (
                                <Tag key={tag} size="small">{tag}</Tag>
                              ))}
                            </div>
                          )}
                          <div style={{ marginTop: 8, fontSize: 11, color: '#666' }}>
                            {rec.image.width}×{rec.image.height} · {formatFileSize(rec.image.file_size || 0)}
                          </div>
                        </div>
                      }
                    />
                  </Card>
                </Col>
              ))}
            </Row>
          )}
        </>
      )}
    </div>
  );
};

export default AIPage;