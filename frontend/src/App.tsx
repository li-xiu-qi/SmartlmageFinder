import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Suspense, lazy } from 'react';
import { ConfigProvider, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import MainLayout from '@/pages/home/components/layout/MainLayout'; // Updated import path

// 页面组件
// 路由页面按需代码分割
const HomePage = lazy(() => import('@/pages/home'));
const ImagesPage = lazy(() => import('@/pages/images/ImagePage'));
const UploadPage = lazy(() => import('@/pages/upload'));
const SearchPage = lazy(() => import('@/pages/search'));
const TagsPage = lazy(() => import('@/pages/tags'));
const SettingsPage = lazy(() => import('@/pages/settings'));
const NotFoundPage = lazy(() => import('@/pages/404'));

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
          <Suspense fallback={<div style={{padding:40,textAlign:'center'}}>加载中...</div>}>
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
          </Suspense>
          
          {/* 全局AI悬浮按钮 - 在所有页面都可见 */}
          <GlobalAIFloatButton />
        </BrowserRouter>
      </AntdApp>
    </ConfigProvider>
  );
}

export default App;
