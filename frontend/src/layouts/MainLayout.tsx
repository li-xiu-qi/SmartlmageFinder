import React, { useState } from 'react';
import { Layout, theme } from 'antd';
import { Outlet } from 'react-router-dom';
import { MainHeader, SideMenu } from '@/pages/home/components/layout';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import './MainLayout.less';

// 从 Layout 组件中解构出 Content 子组件，这样后面可以直接使用 <Content> 而不是 <Layout.Content>
const { Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { systemStatus } = useSystemStatus();
  const { token } = theme.useToken();
  const toggleCollapse = () => setCollapsed(!collapsed);
  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 顶部导航栏 */}
      <MainHeader 
        collapsed={collapsed}
        toggleCollapse={toggleCollapse}
        systemStatus={systemStatus}
      />

      {/* 主体布局容器 - 包含侧边栏和内容区 */}
      <Layout>
        {/* 侧边菜单 */}
        <SideMenu collapsed={collapsed} />

        {/* 内容区布局容器 */}
        <Layout style={{ padding: '0 24px 24px' }}>
          {/* 实际内容显示区域 */}
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: token.colorBgContainer,
              borderRadius: token.borderRadiusLG,
              overflow: 'auto',
            }}
          >
            {/* 路由出口 - 根据当前路由动态渲染组件 */}
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default MainLayout;