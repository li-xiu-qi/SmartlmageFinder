import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import MainLayout from '@/pages/home/components/layout/MainLayout'; // Updated import path

// 页面组件
import HomePage from '@/pages/home';
import ImagesPage from '@/pages/images/ImagePage';
import UploadPage from '@/pages/upload';
import SearchPage from '@/pages/search';
import TagsPage from '@/pages/tags';
import SettingsPage from '@/pages/settings';
import NotFoundPage from '@/pages/404';

// 全局组件
import GlobalAIFloatButton from '@/components/GlobalAIFloatButton';

// 引入全局样式
import './App.less';

function App() {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 4,
        },
      }}
    >
      <AntdApp>
        <BrowserRouter>
          <Routes>
            <Route element={<MainLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="images" element={<ImagesPage />} />
              <Route path="upload" element={<UploadPage />} />
              <Route path="search" element={<SearchPage />} />
              <Route path="tags" element={<TagsPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
          
          {/* 全局AI悬浮按钮 - 在所有页面都可见 */}
          <GlobalAIFloatButton />
        </BrowserRouter>
      </AntdApp>
    </ConfigProvider>
  );
}

export default App;
