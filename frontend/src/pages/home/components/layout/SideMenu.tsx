import React from 'react';
import { Layout, Menu } from 'antd';
import { 
  HomeOutlined, 
  PictureOutlined, 
  UploadOutlined, 
  SearchOutlined, 
  SettingOutlined,
  TagsOutlined 
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { SideMenuProps } from '../../types';

const { Sider } = Layout;

const SideMenu: React.FC<SideMenuProps> = ({ collapsed }) => {
  const navigate = useNavigate();
  const location = useLocation();

  // 获取当前选中的菜单项
  const getSelectedMenuKey = () => {
    const path = location.pathname;
    if (path === '/') return ['home'];
    if (path.startsWith('/images')) return ['images'];
    if (path.startsWith('/upload')) return ['upload'];
    if (path.startsWith('/search')) return ['search'];
    if (path.startsWith('/tags')) return ['tags'];
    if (path.startsWith('/settings')) return ['settings'];
    return ['home'];
  };

  return (
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
  );
};

export default SideMenu;
