/**
 * 全局AI推荐悬浮按钮组件
 * 提供AI图片推荐功能的全局访问
 */

import React, { useState } from 'react';
import { FloatButton } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import AIChatDrawer from '@/components/AIChatDrawer';
// 仅保留一个入口按钮 + 对话抽屉

/**
 * 全局AI推荐悬浮按钮组件
 */
export const GlobalAIFloatButton: React.FC = () => {
  const [chatOpen, setChatOpen] = useState(false);
  // 旧的推荐模式已移除，直接使用对话抽屉

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
