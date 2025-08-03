/**
 * 首页AI功能集成示例
 * 展示如何在首页中集成AI推荐功能的简单按钮
 */

import React from 'react';
import { Button, Space } from 'antd';
import { BulbOutlined } from '@ant-design/icons';
import { useAIRecommendation } from '@/hooks/useAIRecommendation';
import { message } from 'antd';

/**
 * 首页AI推荐功能集成组件
 * 提供快速AI推荐按钮，可以嵌入到现有的首页组件中
 */
const HomeAIIntegration: React.FC = () => {
  const aiRecommendation = useAIRecommendation();

  /**
   * 快速AI推荐预设查询
   */
  const quickRecommendations = [
    { label: '风景照片', query: '推荐一些精美的风景照片' },
    { label: '人物照片', query: '推荐一些人物肖像照片' },
    { label: '动物照片', query: '推荐一些可爱的动物照片' },
  ];

  /**
   * 快速AI推荐
   */
  const handleQuickRecommend = async (query: string, label: string) => {
    message.info(`正在为您推荐${label}...`);
    await aiRecommendation.getRecommendations(query);
    
    if (aiRecommendation.recommendResults) {
      const count = aiRecommendation.recommendResults.images?.length || 0;
      message.success(`已为您推荐 ${count} 张${label}`);
    }
  };

  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ marginBottom: 12 }}>
        <span style={{ fontSize: '16px', fontWeight: 500 }}>🤖 AI智能推荐</span>
      </div>
      
      <Space wrap>
        {quickRecommendations.map((item) => (
          <Button 
            key={item.label}
            icon={<BulbOutlined />}
            onClick={() => handleQuickRecommend(item.query, item.label)}
            loading={aiRecommendation.loading}
            size="small"
          >
            {item.label}
          </Button>
        ))}
      </Space>

      {/* 显示推荐结果数量 */}
      {aiRecommendation.recommendResults && (
        <div style={{ 
          marginTop: 12, 
          padding: '8px 12px', 
          backgroundColor: '#f6ffed', 
          borderRadius: '4px',
          fontSize: '12px',
          color: '#52c41a'
        }}>
          💡 已为您推荐 {aiRecommendation.recommendResults.images?.length || 0} 张图片，
          请使用右下角的AI助手查看详细结果
        </div>
      )}
    </div>
  );
};
export default HomeAIIntegration;

