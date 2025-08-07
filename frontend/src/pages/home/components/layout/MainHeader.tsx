import React from 'react';
import { Layout, Input, Badge, Avatar, Dropdown, Tooltip } from 'antd';
import { SearchOutlined, SettingOutlined, MenuFoldOutlined, MenuUnfoldOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { MainHeaderProps } from '../../types';
import { theme } from 'antd';
import './styles.less';

const { Header } = Layout;
const { Search } = Input;

const MainHeader: React.FC<MainHeaderProps> = ({ collapsed, toggleCollapse, systemStatus }) => {
  const navigate = useNavigate();
  const { token } = theme.useToken();

  // 处理搜索
  const onSearch = (value: string) => {
    if (value.trim()) {
      navigate(`/search?q=${encodeURIComponent(value)}`);
    }
  };  
  // 系统状态指示器
  const statusBadgeColor = 
    systemStatus === 'healthy' 
      ? 'success' 
      : systemStatus === 'error' 
        ? 'error' 
        : 'warning';

  // 设置状态显示文本
  const statusText = 
    systemStatus === 'healthy' 
      ? '正常' 
      : systemStatus === 'error' 
        ? '异常' 
        : '警告';

  // 设置下拉菜单项
  const settingsMenu = {
    items: [
      {
        key: '1',
        label: '系统设置',
        onClick: () => navigate('/settings'),
      },
    ],
  };

  return (
    <Header className="main-header" style={{ background: token.colorBgContainer }}>
      <div className="logo">
        {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
          className: 'trigger',
          onClick: toggleCollapse,
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
      </div>      <div className="header-right">
        <div className="system-status">
          <Tooltip 
            title={systemStatus === 'healthy' ? '系统运行正常' : systemStatus === 'error' ? '系统存在错误' : '系统需要注意'}
            getPopupContainer={(trigger) => trigger.parentElement || document.body}
          >
            <div style={{ display: 'inline-block' }}>
              <Badge status={statusBadgeColor} text={`系统: ${statusText}`} />
            </div>
          </Tooltip>
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
  );
};

export default MainHeader;
