/**
 * AI推荐组件
 * 提供AI智能图片推荐功能
 */

import React, { useState, useCallback } from 'react';
import { Button, Input, Card, List, Avatar, message, Tag, Drawer, Space, Spin } from 'antd';
import { SearchOutlined, BulbOutlined } from '@ant-design/icons';
import { aiRecommendationService } from '@/services/api';
import {
  AIRecommendationParams,
  AIRecommendationData
} from '@/types/recommendation';
import { SearchImageItem } from '@/types/models';

const { TextArea } = Input;

interface AIRecommendationPanelProps {
  visible: boolean;
  onClose: () => void;
  onImageSelect?: (image: SearchImageItem) => void;
}

/**
 * AI推荐面板组件
 */
const AIRecommendationPanel: React.FC<AIRecommendationPanelProps> = ({
  visible,
  onClose,
  onImageSelect
}) => {
  const [loading, setLoading] = useState(false);
  
  // 推荐相关状态
  const [recommendQuery, setRecommendQuery] = useState('');
  const [recommendResults, setRecommendResults] = useState<AIRecommendationData | null>(null);

  /**
   * AI智能推荐
   */
  const handleRecommend = useCallback(async () => {
    if (!recommendQuery.trim()) {
      message.warning('请输入您想要找的图片内容描述');
      return;
    }

    setLoading(true);
    try {
      const params: AIRecommendationParams = {
        user_query: recommendQuery,
        vector_targets: ['title', 'description', 'image'],
        limit: 20
      };

      const response = await aiRecommendationService.getRecommendations(params);
      
      if (response.status === 'success' && response.data) {
        setRecommendResults(response.data);
        
        // 显示查询改写信息
        if (response.data.query_rewrite) {
          const { original_query, optimized_query, rewrite_success } = response.data.query_rewrite;
          if (rewrite_success && original_query !== optimized_query) {
            message.info(`AI已优化您的搜索：${original_query} → ${optimized_query}`);
          }
        }
      } else {
        message.error(response.message || 'AI推荐服务出错');
      }
    } catch (error: any) {
      console.error('AI推荐错误:', error);
      message.error(error.message || 'AI推荐服务暂时不可用');
    } finally {
      setLoading(false);
    }
  }, [recommendQuery]);

  /**
   * 渲染推荐内容
   */
  const renderRecommendContent = () => (
    <div>
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <div>
          <p>💡 <strong>AI智能推荐</strong></p>
          <p>用自然语言描述您想要找的图片，AI会为您推荐最匹配的内容。</p>
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              placeholder="例如：我想看一些山水风景、给我找点城市夜景、有没有可爱的动物照片..."
              value={recommendQuery}
              onChange={(e) => setRecommendQuery(e.target.value)}
              rows={2}
            />
            <Button 
              type="primary" 
              icon={<SearchOutlined />}
              onClick={handleRecommend}
              loading={loading}
            >
              智能推荐
            </Button>
          </Space.Compact>
        </div>

        {recommendResults && (
          <Card title={`为您推荐 ${recommendResults.images?.length || 0} 张图片`} size="small">
            {recommendResults.query_rewrite && (
              <div style={{ marginBottom: 16, padding: 8, background: '#f6ffed', borderRadius: 4 }}>
                <BulbOutlined style={{ color: '#52c41a', marginRight: 8 }} />
                <span style={{ fontSize: '12px', color: '#666' }}>
                  AI查询优化：{recommendResults.query_rewrite.original_query} 
                  {recommendResults.query_rewrite.rewrite_success && 
                   recommendResults.query_rewrite.original_query !== recommendResults.query_rewrite.optimized_query && 
                   ` → ${recommendResults.query_rewrite.optimized_query}`}
                </span>
              </div>
            )}
            
            <List
              dataSource={recommendResults.images || []}
              renderItem={(item) => (
                <List.Item
                  key={item.id}
                  style={{ cursor: 'pointer' }}
                  onClick={() => onImageSelect?.(item)}
                >
                  <List.Item.Meta
                    avatar={<Avatar src={(item as any).public_url || (item as any).filepath || undefined} shape="square" size={48} />}
                    title={item.title}
                    description={
                      <div>
                        <div>{item.description}</div>
                        <div style={{ marginTop: 4 }}>
                          {item.tags.slice(0, 3).map(tag => (
                            <Tag key={tag}>{tag}</Tag>
                          ))}
                          {item.score && <span style={{ color: '#999', fontSize: '12px' }}>相关度: {(item.score * 100).toFixed(1)}%</span>}
                        </div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        )}
      </Space>
    </div>
  );

  return (
    <Drawer
      title="AI智能推荐"
      placement="right"
      width={480}
      onClose={onClose}
      open={visible}
    >
      <Spin spinning={loading}>
        {renderRecommendContent()}
      </Spin>
    </Drawer>
  );
};

export default AIRecommendationPanel;
