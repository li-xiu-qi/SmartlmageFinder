import React, { useState, useEffect } from 'react';
import { Layout, Menu, theme, Input, Badge, Avatar, Dropdown, Button, message, Modal } from 'antd';
import { 
  HomeOutlined, 
  PictureOutlined, 
  UploadOutlined, 
  SearchOutlined, 
  SettingOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  TagsOutlined,
  ExclamationCircleFilled
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { systemService } from '@/services/api';
import './MainLayout.less';

const { Header, Sider, Content } = Layout;
const { Search } = Input;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [systemStatus, setSystemStatus] = useState<{status?: string}>({});
  const [clearingCache, setClearingCache] = useState(false);
  const [confirmModalVisible, setConfirmModalVisible] = useState(false);
  
  const navigate = useNavigate();
  const location = useLocation();
  const { token } = theme.useToken();

  // 获取系统状态
  useEffect(() => {
    const fetchSystemStatus = async () => {
      try {
        const response = await systemService.getSystemStatus();
        if (response.status === 'success' && response.data) {
          setSystemStatus({
            status: response.data.system.status
          });
        }
      } catch (error) {
        console.error('获取系统状态失败:', error);
        setSystemStatus({
          status: 'error'
        });
      }
    };

    fetchSystemStatus();
    // 每5分钟更新一次系统状态
    const interval = setInterval(fetchSystemStatus, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // 获取当前选中的菜单项
  const getSelectedMenuKey = () => {
    const path = location.pathname;
    if (path === '/') return ['home'];
    if (path.startsWith('/images')) return ['images'];
    if (path.startsWith('/upload')) return ['upload'];
    if (path.startsWith('/search')) return ['search'];
    if (path.startsWith('/settings')) return ['settings'];
    return ['home'];
  };

  // 处理搜索
  const onSearch = (value: string) => {
    if (value.trim()) {
      navigate(`/search?q=${encodeURIComponent(value)}`);
    }
  };

  // 系统状态指示器
  const statusBadgeColor = 
    systemStatus.status === 'healthy' 
      ? 'green' 
      : systemStatus.status === 'error' 
        ? 'red' 
        : 'orange';

  // 处理清除缓存确认
  const showClearCacheConfirm = () => {
    setConfirmModalVisible(true);
  };

  // 确认清除缓存
  const handleConfirmClearCache = async () => {
    try {
      setClearingCache(true);
      const response = await systemService.clearCache(['all']);
      
      if (response.status === 'success') {
        message.success('缓存已成功清除');
      } else {
        message.error(response.error?.message || '清除缓存失败');
      }
    } catch (error: any) {
      console.error('清除缓存失败:', error);
      message.error(`清除缓存失败: ${error.message || '未知错误'}`);
    } finally {
      setClearingCache(false);
      setConfirmModalVisible(false);
    }
  };

  // 取消清除缓存
  const handleCancelClearCache = () => {
    setConfirmModalVisible(false);
  };

  // 设置下拉菜单项
  const settingsMenu = {
    items: [
      {
        key: '1',
        label: '系统设置',
        onClick: () => navigate('/settings'),
      },
      {
        key: '2',
        label: clearingCache ? '正在清除缓存...' : '清除缓存',
        onClick: showClearCacheConfirm,
        disabled: clearingCache,
      },
    ],
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header className="main-header" style={{ background: token.colorBgContainer }}>
        <div className="logo">
          {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
            className: 'trigger',
            onClick: () => setCollapsed(!collapsed),
          })}
          <h1>SmartImageFinder</h1>
        </div>
        
        <div className="header-search">
          <Search
            placeholder="搜索图片..."
            allowClear
            enterButton={<SearchOutlined />}
            size="middle"
            onSearch={onSearch}
          />
        </div>

        <div className="header-right">
          <div className="system-status">
            <Badge status={statusBadgeColor as any} text={`系统: ${systemStatus.status || '加载中'}`} />
          </div>

          <Dropdown menu={settingsMenu} placement="bottomRight">
            <Avatar 
              icon={<SettingOutlined />} 
              style={{ 
                backgroundColor: token.colorPrimary,
                cursor: 'pointer'
              }}
            />
          </Dropdown>
        </div>
      </Header>

      <Layout>
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          theme="light"
          width={200}
          collapsedWidth={80}
        >
          <Menu
            mode="inline"
            selectedKeys={getSelectedMenuKey()}
            style={{ height: '100%', borderRight: 0 }}
            items={[
              {
                key: 'home',
                icon: <HomeOutlined />,
                label: '首页',
                onClick: () => navigate('/'),
              },
              {
                key: 'images',
                icon: <PictureOutlined />,
                label: '图片管理',
                onClick: () => navigate('/images'),
              },
              {
                key: 'upload',
                icon: <UploadOutlined />,
                label: '上传图片',
                onClick: () => navigate('/upload'),
              },
              {
                key: 'search',
                icon: <SearchOutlined />,
                label: '搜索',
                onClick: () => navigate('/search'),
              },
              {
                key: 'tags',
                icon: <TagsOutlined />,
                label: '标签管理',
                onClick: () => navigate('/tags'),
              },
              {
                key: 'settings',
                icon: <SettingOutlined />,
                label: '系统设置',
                onClick: () => navigate('/settings'),
              },
            ]}
          />
        </Sider>

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

      {/* 清除缓存确认对话框 */}
      <Modal
        title={
          <span>
            <ExclamationCircleFilled style={{ color: '#faad14', marginRight: 8 }} />
            确认清除缓存
          </span>
        }
        open={confirmModalVisible}
        onOk={handleConfirmClearCache}
        onCancel={handleCancelClearCache}
        confirmLoading={clearingCache}
        okText="确认清除"
        cancelText="取消"
        okButtonProps={{ danger: true }}
      >
        <p>清除缓存将删除所有向量缓存数据，可能会导致下次搜索速度变慢。确定要继续吗？</p>
      </Modal>
    </Layout>
  );
};

export default MainLayout;