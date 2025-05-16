import React, { useState } from 'react';
import { Layout, theme } from 'antd';
import { Outlet } from 'react-router-dom';
import { MainHeader, SideMenu } from '@/pages/home/components/layout';
import { useSystemStatus } from '@/hooks/useSystemStatus';
import './MainLayout.less';

const { Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { systemStatus } = useSystemStatus();
  const { token } = theme.useToken();

  const toggleCollapse = () => setCollapsed(!collapsed);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <MainHeader 
        collapsed={collapsed}
        toggleCollapse={toggleCollapse}
        systemStatus={systemStatus}
      />

      <Layout>
        <SideMenu collapsed={collapsed} />

        <Layout style={{ padding: '0 24px 24px' }}>
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
            <Outlet />
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

export default MainLayout;