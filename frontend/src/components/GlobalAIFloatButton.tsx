/**
 * 全局AI推荐悬浮按钮组件
 * 提供AI图片推荐功能的全局访问
 */

import React, { useState } from 'react';
import { FloatButton } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import AIChatDrawer from '@/components/AIChatDrawer';

/**
 * 全局AI推荐悬浮按钮组件
 */
export const GlobalAIFloatButton: React.FC = () => {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <>
      <FloatButton
        icon={<RobotOutlined />}
        tooltip="AI图片推荐（对话）"
        onClick={() => setChatOpen(true)}
        style={{ 
          right: 24, 
          bottom: 24,
          width: 60,
          height: 60
        }}
      />
  <AIChatDrawer open={chatOpen} onClose={()=> setChatOpen(false)} />
    </>
  );
};

export default GlobalAIFloatButton;
