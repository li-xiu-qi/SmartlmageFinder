import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import MainLayout from '@/layouts/MainLayout';

// 页面组件
import HomePage from '@/pages/home';
import ImagesPage from '@/pages/images';
import ImageDetailPage from '@/pages/images/detail';
import UploadPage from '@/pages/upload';
import SearchPage from '@/pages/search';
import TagsPage from '@/pages/tags';
import SettingsPage from '@/pages/settings';
import NotFoundPage from '@/pages/404';

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
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<HomePage />} />
            <Route path="images" element={<ImagesPage />} />
            <Route path="images/:uuid" element={<ImageDetailPage />} />
            <Route path="upload" element={<UploadPage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="tags" element={<TagsPage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
